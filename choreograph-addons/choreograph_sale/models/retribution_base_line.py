# -*- coding: utf-8 -*-

from odoo import fields, models


class RetributionBaseLine(models.Model):
    _name = 'retribution.base.line'
    _description = 'Retribution Base Line'

    multi_base_id = fields.Many2one('retribution.base', 'Multi-Base')
    base_id = fields.Many2one('retribution.base', 'Base')
    volume = fields.Integer('Volume')
    volume_percentage = fields.Float('%vol')
    retribution_percentage = fields.Float('%retribution')
