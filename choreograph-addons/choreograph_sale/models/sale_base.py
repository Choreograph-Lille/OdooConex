# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class SaleBase(models.Model):
    _name = 'sale.base.concerned'

    name = fields.Char('Name')
    reason = fields.Char('Reason')
    is_closed_base = fields.Boolean('Closed base')
    volume_percentage = fields.Float('Volume percentage')
    retribution_percentage = fields.Float('Retribution percentage')
