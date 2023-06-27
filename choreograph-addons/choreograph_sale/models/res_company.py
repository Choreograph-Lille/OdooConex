# -*- coding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    invoice_terms_c9h = fields.Html("Invoice Default Terms and Conditions", translate=True)