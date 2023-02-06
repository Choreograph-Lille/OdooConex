# -*- coding: utf-8 -*-

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    concerned_base = fields.Many2one('retribution.base', 'Retribution Base')
