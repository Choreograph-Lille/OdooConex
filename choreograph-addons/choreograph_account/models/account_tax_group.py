# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountTaxGroup(models.Model):
    _inherit = "account.tax.group"

    preceding_subtotal = fields.Char(translate=True)
