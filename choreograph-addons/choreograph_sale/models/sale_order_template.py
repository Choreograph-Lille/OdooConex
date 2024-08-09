# -*- coding: utf-8 -*-


from odoo import api, fields, models, _

class SaleOrderTemplate(models.Model):
    
    _inherit = "sale.order.template"

    with_rent = fields.Boolean()
    minimal_consumption = fields.Integer()
    minimal_price = fields.Float()
    cost_per_thousand = fields.Float()