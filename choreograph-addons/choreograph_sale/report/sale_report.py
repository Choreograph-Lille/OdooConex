from odoo import fields, models, api


CUSTOM_STATE_SEQUENCE_MAP = {
    'forecast': 0,
    'lead': 1,
    'prospecting': 2,
    'qualif': 3,
    'draft': 4,
    'sent': 5,
    'sale': 6,
    'done': 7,
    'closed_won': 8,
    'adjustment': 9,
    'cancel': 10
}


class SaleReport(models.Model):
    _inherit = 'sale.report'

    retribution = fields.Float(readonly=True)
    state_specific = fields.Selection([
        ('forecast', 'Forecast'),
        ('lead', 'Lead'),
        ('prospecting', 'Prospecting'),
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('closed_won', 'Closed Won'),
        ('adjustment', 'Adjustment'),
        ('cancel', 'Cancelled'),
    ], string="C9H State", default="forecast")

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

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(SaleReport, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'state_specific' in groupby:
            return sorted(res, key=lambda g: CUSTOM_STATE_SEQUENCE_MAP.get(g.get('state_specific'), 1000))
        return res
