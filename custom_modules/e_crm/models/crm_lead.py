from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    minimum_revenue_before_vat = fields.Float(string='Doanh thu tối thiểu trước thuế')