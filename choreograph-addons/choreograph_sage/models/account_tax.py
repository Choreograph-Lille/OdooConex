# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = "account.tax"

    tva_profile_code = fields.Char()
