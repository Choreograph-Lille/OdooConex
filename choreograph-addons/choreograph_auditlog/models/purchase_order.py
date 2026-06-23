from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    is_retribution_order = fields.Boolean(compute='_compute_is_retribution_order', store=True)

    @api.depends('order_line')
    def _compute_is_retribution_order(self):
        for order in self:
            if order.order_line.filtered(lambda line: line.product_id.retribution):
                order.is_retribution_order = True
            else:
                order.is_retribution_order = False
            
