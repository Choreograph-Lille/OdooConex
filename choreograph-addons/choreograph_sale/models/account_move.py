# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import is_html_empty


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.depends('move_type', 'partner_id', 'company_id')
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
                lang = move.partner_id.lang or self.env.user.lang
                if not move.company_id.terms_type == 'html':
                    narration = move.company_id.with_context(lang=lang).invoice_terms_c9h if not is_html_empty(
                        move.company_id.invoice_terms_c9h) else ''
                else:
                    baseurl = self.env.company.get_base_url() + '/terms'
                    context = {'lang': lang}
                    narration = _('Terms & Conditions: %s', baseurl)
                    del context
                move.narration = narration or False
