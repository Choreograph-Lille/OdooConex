# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    concerned_base = fields.Many2one('retribution.base', 'Retribution Base')
