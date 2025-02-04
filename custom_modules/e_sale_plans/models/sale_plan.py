from pkg_resources import require
from reportlab.lib.randomtext import subjects
from requests_toolbelt.multipart.encoder import total_len

from odoo import models, fields, api

from odoo.exceptions import UserError
from odoo.modules.module import current_test


class SalePlan(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'e.sale.plan'
    _description = 'Kế hoạch bán hàng'

    name = fields.Char(string='Tên kế hoạch')
    quotation_id = fields.Many2one('sale.order', string='Báo giá', readonly=True)
    sale_plan_info = fields.Char(string='Thông tin kế hoạch')
    sale_plan_approver_lines = fields.One2many('e.sale.plan.approver', 'sale_plan_id', string='Duyệt kế hoạch')
    state = fields.Selection([
        ('new', 'Mới'),
        ('send_to_approver', 'Gửi Duyệt'),
        ('approved', 'Duyệt'),
        ('rejected', 'Từ chối Duyệt'),
    ], string='Trạng thái', default='new')



    def action_send_to_approver(self):
        self.ensure_one()
        # current_user = self.env.user
        approvers = self.sale_plan_approver_lines.mapped('approver_id')
        for approver_line in self.sale_plan_approver_lines:
            approver_line.state = 'send_to_approver'
        for approver in approvers:
            if approver:
                self.message_post(
                    body = f"Cần xem xét kế hoạch bán hàng: {self.name}",
                    subject = 'Yêu cầu phê duyệt kế hoạch bán hàng',
                    partner_ids = [approver.id],
                    message_type = 'notification',
                )
                self.state = 'send_to_approver'

    def _update_plan_state(self):
        for plan in self:
            approver_states = plan.sale_plan_approver_lines.mapped('state')
            approved_count = approver_states.count('approved')
            rejected_count = approver_states.count('rejected')
            total_approvers = len(plan.sale_plan_approver_lines)

            if approved_count == total_approvers:
                plan.state = 'approved'
            elif rejected_count == total_approvers:
                plan.state = 'rejected'
            else:
                plan.state = 'new'
                creator_partner = plan.create_uid.partner_id
                if creator_partner:
                    plan.message_post(
                        body=f"Kế hoạch bán hàng: {plan.name} chưa được duyệt hoàn toàn. Vui lòng xem lại kế hoạch.",
                        subject='Kế hoạch chưa được duyệt',
                        partner_ids=[creator_partner.id],
                        message_type='notification',
                    )


class SalePlanApprover(models.Model):
    _name = 'e.sale.plan.approver'
    _description = 'Danh Sách Người Phê Duyệt'

    sale_plan_id = fields.Many2one('e.sale.plan', string='Kế hoạch bán hàng')
    approver_id = fields.Many2one('res.partner', string='Người duyệt')
    # approve_date = fields.Date(string='Ngày duyệt')
    state = fields.Selection([
        ('send_to_approver', 'Gửi duyệt'),
        ('approved', 'Duyệt'),
        ('rejected', 'Từ chối')

    ], string='Trạng thái', default='')
    approve_note = fields.Text(string='Ghi chú')

    @api.model
    def create(self, vals):

        sale_plan = self.env['e.sale.plan'].browse(vals.get('sale_plan_id'))
        if sale_plan.create_uid != self.env.user:
            raise UserError('Chỉ người tạo kế hoạch mới có thể thêm người duyệt.')

        return super(SalePlanApprover, self).create(vals)

    def write(self, vals):
        result = super(SalePlanApprover, self).write(vals)
        if 'state' in vals:
            self.sale_plan_id._update_plan_state()
        return result

    def action_approve(self):
        current_user = self.env.user
        if self.approver_id.id != current_user.partner_id.id:
            raise UserError('Bạn không thể duyệt cho người khác.')
        self.state = 'approved'
        self.sale_plan_id._update_plan_state()

        creator_partner = self.sale_plan_id.create_uid.partner_id
        if creator_partner:
            self.sale_plan_id.message_post(
                body=f"{current_user.name} đã duyệt kế hoạch bán hàng: {self.sale_plan_id.name}.",
                subject='Duyệt kế hoạch bán hàng',
                partner_ids=[creator_partner.id],
                message_type='notification',
            )

    def action_reject(self):
        current_user = self.env.user
        if self.approver_id.id != current_user.partner_id.id:
            raise UserError('Bạn không thể từ chối cho người khác.')
        self.state = 'rejected'
        self.sale_plan_id._update_plan_state()

        creator_partner = self.sale_plan_id.create_uid.partner_id
        if creator_partner:
            self.sale_plan_id.message_post(
                body=f"{current_user.name} đã từ chối duyệt kế hoạch bán hàng: {self.sale_plan_id.name}.",
                subject='Từ chối kế hoạch bán hàng',
                partner_ids=[creator_partner.id],
                message_type='notification',
            )


