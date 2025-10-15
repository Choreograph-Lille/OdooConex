from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    retribution = fields.Boolean(related='product_tmpl_id.retribution',store=True)