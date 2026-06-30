from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pricelist_currency_id = fields.Many2one('res.currency', related='property_product_pricelist.currency_id')
    is_confidential = fields.Boolean(default=False)
    siren = fields.Char(string="SIREN")
    electronic_address = fields.Char("Electronic Address", tracking=True)
    pf_code_identification = fields.Char("PF Code Identification", tracking=True)

    def update_confidential_document(self):
        confidential_partners = self.env['res.partner'].search([('is_confidential', '=', True)])
        for partner in confidential_partners:
           
            # Update purchase order documents
            purchase_orders = self.env['purchase.order'].search([('partner_id', '=', partner.id)])
            if purchase_orders:
                for order in purchase_orders:
                    order.write({
                        'is_confidential': True
                    })
            # Update invoices documents
            invoices = self.env['account.move'].search([
                ('partner_id', '=', partner.id),
                ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund']),
                ('is_confidential', '=', False)
            ])
            for invoice in invoices:
                invoice.write({
                    'is_confidential': True
                })

