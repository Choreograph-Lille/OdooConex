# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleDataConservation(models.Model):
    _name = 'sale.data.conservation'

    name = fields.Char()
