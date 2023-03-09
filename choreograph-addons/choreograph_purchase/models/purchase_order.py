from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_approve = fields.Datetime('Order Date')
