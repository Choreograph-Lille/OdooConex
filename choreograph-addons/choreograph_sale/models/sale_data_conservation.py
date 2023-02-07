# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleDataConservation(models.Model):
    _name = 'sale.data.conservation'

    name = fields.Char(translate=True)
