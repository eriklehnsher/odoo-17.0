from odoo import models, fields, api



class CrmTeam(models.Model):
    _inherit = 'crm.team'


    target_jan = fields.Float(string='Tháng 1')
    target_feb = fields.Float(string='Tháng 2')
    target_mar = fields.Float(string='Tháng 3')
    target_apr = fields.Float(string='Tháng 4')
    target_may = fields.Float(string='Tháng 5')
    target_jun = fields.Float(string='Tháng 6')
    target_jul = fields.Float(string='Tháng 7')
    target_aug = fields.Float(string='Tháng 8')
    target_sep = fields.Float(string='Tháng 9')
    target_oct = fields.Float(string='Tháng 10')
    target_nov = fields.Float(string='Tháng 11')
    target_dec = fields.Float(string='Tháng 12')

    @api.constrains('target_jan', 'target_feb', 'target_mar',
                    'target_apr', 'target_may', 'target_jun',
                    'target_jul', 'target_aug', 'target_sep',
                    'target_oct', 'target_nov', 'target_dec')

    def _check_target(self):
        for record in self:
            targets = [
                record.target_jan,
                record.target_feb,
                record.target_mar,
                record.target_apr,
                record.target_may,
                record.target_jun,
                record.target_jul,
                record.target_aug,
                record.target_sep,
                record.target_oct,
                record.target_nov,
                record.target_dec
            ]
            for target in targets:
                if target is None or target < 0:
                    raise ValueError('Mục tiêu không thể nhỏ hơn 0')