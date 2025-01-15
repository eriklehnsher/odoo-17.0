from pkg_resources import require
from reportlab.lib.randomtext import subjects

from odoo import models, fields, api

from odoo.exceptions import UserError
from odoo.modules.module import current_test


class SalePlan(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'e.sale.plan'
    _description = 'Kế hoạch bán hàng'

    name = fields.Char(string='Tên kế hoạch')
    quotation_id = fields.Many2one('sale.order', string='Báo giá', readonly=True)
    sale_plan_info = fields.Char(string='Thông tin kế hoạch',required=True)
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
            if all (approver.state == 'approved' for approver in plan.sale_plan_approver_lines):
                plan.state = 'approved'
            elif any(approver.state == 'rejected' for approver in plan.sale_plan_approver_lines):
                plan.state = 'rejected'
            else:
                plan.state = 'send_to_approver'


class SalePlanApprover(models.Model):
    _name = 'e.sale.plan.approver'
    _description = 'Danh Sách Người Phê Duyệt'

    sale_plan_id = fields.Many2one('e.sale.plan', string='Kế hoạch bán hàng')
    approver_id = fields.Many2one('res.partner', string='Người duyệt')
    # approve_date = fields.Date(string='Ngày duyệt')
    state = fields.Selection([

        ('approved', 'Duyệt'),
        ('not_approved_yet', 'Chưa duyệt'),
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
        self.state = 'approved'
        self.sale_plan_id._update_plan_state()
        current_user = self.env.user
        creator_partner = self.sale_plan_id.create_uid.partner_id
        print('Người Tạo kế hoạch: ',creator_partner)
        if creator_partner:
            self.sale_plan_id.message_post(
                body=f"{current_user.name} Đã duyệt kế hoạch bán hàng: {self.sale_plan_id.name}",
                subject='Duyệt kế hoạch bán hàng',
                partner_ids=[creator_partner.id],
                message_type='notification',
            )

    def action_reject(self):
        self.state = 'rejected'
        self.sale_plan_id.state = 'rejected'
        current_user  = self.env.user
        creator_partner = self.sale_plan_id.create_uid.partner_id
        if creator_partner:
            self.sale_plan_id.message_post(
                body=f"{current_user.name} Đã từ chối duyệt kế hoạch bán hàng: {self.sale_plan_id.name}",
                subject='Từ chối duyệt kế hoạch bán hàng',
                partner_ids=[creator_partner.id],
                message_type='notification',
            )

