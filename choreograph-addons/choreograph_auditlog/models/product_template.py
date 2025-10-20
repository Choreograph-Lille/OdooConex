from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    retribution = fields.Boolean(default=False)
    mymodel = fields.Boolean(default=False)
