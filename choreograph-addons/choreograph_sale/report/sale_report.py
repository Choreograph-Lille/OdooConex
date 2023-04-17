from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    retribution = fields.Float(readonly=True)
    state_specific = fields.Selection([
        ('forecast', 'Forecast'),
        ('lead', 'Lead'),
        ('prospecting', 'Prospecting'),
        ('qualif', 'Qualif'),
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], default='forecast')

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res.update({
            'retribution': 'l.retribution_cost',
            'state_specific': 's.state_specific',
        })
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += ',l.retribution_cost,s.state_specific'
        return res
