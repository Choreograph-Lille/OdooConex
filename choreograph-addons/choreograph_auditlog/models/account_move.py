from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    is_mymodel = fields.Boolean(compute='_compute_is_mymodel', store=True)

    def update_subscription_invoices(self):
        subscriptions = self.env['sale.order'].search([('state', '=', 'sale'), ('is_subscription', '=', True)])
        if subscriptions:
            invoice_ids = subscriptions.invoice_ids
            invoice_ids._compute_is_mymodel()
        

    @api.depends('invoice_line_ids')
    def _compute_is_mymodel(self):
        for order in self:
            if order.move_type == 'out_invoice' and order.invoice_line_ids.filtered(lambda line: line.product_id.mymodel):
                order.is_mymodel = True
            else:
                order.is_mymodel = False
