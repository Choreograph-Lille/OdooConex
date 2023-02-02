from odoo import fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    retribution = fields.Float(readonly=True)

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['retribution'] = "l.retribution_cost"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        res += ',l.retribution_cost'
        return res
