# -*- coding: utf-8 -*-

from odoo import models

class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    def _compute_terms(
        self, 
        date_ref, 
        currency, 
        company, tax_amount, 
        tax_amount_currency, 
        sign, 
        untaxed_amount, 
        untaxed_amount_currency, 
        cash_rounding=None
    ):

        provider_invoice_date = self.env.context.get('provider_invoice_date')
        if provider_invoice_date:
            date_ref = provider_invoice_date

        return super()._compute_terms(
            date_ref=date_ref,
            currency=currency,
            tax_amount_currency=tax_amount_currency,
            tax_amount=tax_amount,
            untaxed_amount_currency=untaxed_amount_currency,
            untaxed_amount=untaxed_amount,
            company=company,
            cash_rounding=cash_rounding,
            sign=sign,
        )
    