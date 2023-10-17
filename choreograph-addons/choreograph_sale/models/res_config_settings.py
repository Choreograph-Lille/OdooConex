# -*- coding: utf-8 -*-

from odoo import fields, models



class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"


    use_invoice_terms_c9h = fields.Boolean(
        string="Invoice Terms & Conditions",
        config_parameter="invoice.terms.conditions",
        default=True)
    invoice_terms_c9h = fields.Html(related="company_id.invoice_terms_c9h", string="Invoice Terms & Conditions", readonly=False)
