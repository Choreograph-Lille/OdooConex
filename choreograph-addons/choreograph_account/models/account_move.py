# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
TYPE_REVERSE_MAP = {
    'entry': 'entry',
    'out_invoice': 'out_refund',
    'out_refund': 'entry',
    'in_invoice': 'in_refund',
    'in_refund': 'entry',
    'out_receipt': 'out_refund',
    'in_receipt': 'in_refund',
}

from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_order_id = fields.Many2one("sale.order", "Sale Order", compute="_compute_sale_order_id", store=True, compute_sudo=True)
    user_id = fields.Many2one('res.users', tracking=False)
    is_confidential = fields.Boolean()
    provider_invoice_date = fields.Date()

    def action_invoice_sent(self):
        result = super(AccountMove, self).action_invoice_sent()
        template = self.env.ref("choreograph_account.email_template_edi_invoice", raise_if_not_found=False)
        result["context"].update({
            "default_use_template": bool(template),
            "default_template_id": template and template.id or False,
        })

        return result
    @api.depends('move_type', 'provider_invoice_date')
    def _compute_needed_terms(self):
        for invoice in self:
            if invoice.move_type == 'in_invoice' and invoice.provider_invoice_date:
                invoice = invoice.with_context(
                    provider_invoice_date=invoice.provider_invoice_date
                )
            super(AccountMove, invoice)._compute_needed_terms()
    
    @api.depends('move_type', 'provider_invoice_date')
    def _compute_invoice_date_due(self):
        for move in self:
            if move.move_type == 'in_invoice' and move.provider_invoice_date:
                # If provider_invoice_date is set, use it to compute invoice_date_due
                terms = move.needed_terms
                if terms:
                    move.invoice_date_due = terms and max(
                    (k['date_maturity'] for k in terms.keys() if k),
                    default=False,)
                else:
                    move.invoice_date_due = move.provider_invoice_date
            else:
                super(AccountMove, move)._compute_invoice_date_due()

    @api.depends('line_ids.sale_line_ids')
    def _compute_sale_order_id(self):
        for move in self:
            orders = move.line_ids.mapped("sale_line_ids").mapped("order_id")
            move.sale_order_id = orders and orders[0].id or False

    @api.model
    def _get_mail_partner(self):
        adresses = self.partner_id
        if self.partner_id.child_ids:
            adresses |= self.partner_id.child_ids.filtered(lambda rp: rp.type == 'invoice')
        return ','.join([str(rp.id) for rp in adresses])

    def _reverse_moves(self, default_values_list=None, cancel=False):
        ''' Override _reverse_moves function
        :return: An account.move recordset, reverse of the current self without posted.
        '''
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_moves = self.env['account.move']
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'move_type': TYPE_REVERSE_MAP[move.move_type],
                'reversed_entry_id': move.id,
                'partner_id': move.partner_id.id,
            })
            reverse_moves += move.with_context(
                move_reverse_cancel=cancel,
                include_business_fields=True,
                skip_invoice_sync=move.move_type == 'entry',
            ).copy(default_values)

        reverse_moves.with_context(skip_invoice_sync=cancel).write({'line_ids': [
            Command.update(line.id, {
                'balance': -line.balance,
                'amount_currency': -line.amount_currency,
            })
            for line in reverse_moves.line_ids
            if line.move_id.move_type == 'entry' or line.display_type == 'cogs'
        ]})
        
        return reverse_moves
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.is_confidential = self.partner_id.is_confidential    
        if self.partner_id.property_product_pricelist:
            self.currency_id = self.partner_id.property_product_pricelist.currency_id
    