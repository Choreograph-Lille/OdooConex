from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pricelist_currency_id = fields.Many2one('res.currency', related='property_product_pricelist.currency_id')
