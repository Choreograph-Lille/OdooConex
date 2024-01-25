# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ResPartner(models.Model):
    _inherit = "resource.calendar.leaves"

    country_base = fields.Selection([("uk", "UK"), ("fr", "FR")], "Country Base", tracking=True)

