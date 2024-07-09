# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import is_html_empty


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_lang_and_currency(self):  
        if self.env.ref('base.EUR') and self.currency_id == self.env.ref('base.EUR'):
            lang = 'fr_FR'
            currency_id = self.env.ref('base.EUR')
        elif self.env.ref('base.GBP') and self.currency_id == self.env.ref('base.GBP'):
            lang = 'en_GB'
            currency_id = self.env.ref('base.GBP')
        else:
            lang = self.partner_id.lang or self.env.user.lang
            currency_id = False
        return lang, currency_id
    
    @api.depends('move_type', 'partner_id', 'company_id', 'currency_id')
    def _compute_narration(self):
        """
        Same as native, but instead use 'invoice.terms.conditions' and 'invoice_terms_c9h'
        :return:
        """
        use_invoice_terms = self.env['ir.config_parameter'].sudo().get_param('invoice.terms.conditions')
        for move in self:
            if not move.is_sale_document(include_receipts=True):
                continue
            if not use_invoice_terms:
                move.narration = False
            else:
                lang, currency_id = move._get_lang_and_currency()
                if not move.company_id.terms_type == 'html':
                    narration = move.company_id.with_context(lang=lang).invoice_terms_c9h if (
                        not is_html_empty(move.company_id.invoice_terms_c9h) and 
                        currency_id
                    ) else ''
                else:
                    baseurl = self.env.company.get_base_url() + '/terms'
                    context = {'lang': lang}
                    narration = _('Terms & Conditions: %s', baseurl)
                    del context
                move.narration = narration or False
