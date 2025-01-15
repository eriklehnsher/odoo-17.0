from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import raise_error


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_plan_id = fields.Many2one('e.sale.plan', string='Kế hoạch bán hàng')

    def action_create_plan_sale_order(self):
        self.ensure_one()
        if self.state not in ['draft', 'sent']:
            raise UserError('Chỉ có thể tạo kế hoạch bán hàng cho báo giá chưa được xác nhận.')

        self.sale_plan_id = self.env['e.sale.plan'].create({
            'name': 'Kế hoạch bán hàng cho đơn hàng ' + self.name,
            'quotation_id': self.id,
            # 'sale_plan_info': self.note,
            'state': 'new',
        })
        return {
            # 'name': 'Kế hoạch bán hàng',
            'view_mode': 'form',
            'res_model': 'e.sale.plan',
            'type': 'ir.actions.act_window',
            'res_id': self.sale_plan_id.id,
            'target': 'current',
        }

    def action_confirm(self):
        for order in self:
            if order.sale_plan_id:
                if order.sale_plan_id.state != 'approved':
                    raise UserError('Không thể xác nhận báo giá khi kế hoạch bán hàng chưa được duyệt.')
            approve_plan_exists = any(plan.state == 'approved' for plan in order.sale_plan_id)
            if not approve_plan_exists:
                raise UserError('Không thể xác nhận báo giá khi chưa tạo kế hoạch bán hàng.')
        return super(SaleOrder, self).action_confirm()