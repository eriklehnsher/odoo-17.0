from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sale_plan_ids = fields.One2many('e.sale.plan', 'quotation_id', string='Kế hoạch bán hàng')

    def action_create_plan_sale_order(self):
        self.ensure_one()
        if self.state not in ['draft', 'sent']:
            raise UserError('Chỉ có thể tạo kế hoạch bán hàng cho báo giá chưa được xác nhận.')

        sale_plan = self.env['e.sale.plan'].create({
            'name': f'Kế hoạch bán hàng cho đơn hàng {self.name}',
            'quotation_id': self.id,
            'state': 'new',
        })
        self.sale_plan_ids += sale_plan

        return {
            'view_mode': 'form',
            'res_model': 'e.sale.plan',
            'type': 'ir.actions.act_window',
            'res_id': sale_plan.id,
            'target': 'current',
        }

    def action_confirm(self):
        for order in self:
            if not order.sale_plan_ids:
                raise UserError('Không thể xác nhận báo giá khi chưa có kế hoạch bán hàng.')
            approved_plan_exists = any(plan.state == 'approved' for plan in order.sale_plan_ids)
            if not approved_plan_exists:
                raise UserError('Không thể xác nhận báo giá khi không có kế hoạch bán hàng nào được duyệt.')
        return super(SaleOrder, self).action_confirm()
