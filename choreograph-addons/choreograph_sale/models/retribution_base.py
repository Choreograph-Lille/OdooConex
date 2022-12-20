# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class RetributionBase(models.Model):
    _name = 'retribution.base'
    _description = 'Retribution base'

    name = fields.Char('Name', required=True)
    is_open = fields.Boolean('Open')
    is_multi_base = fields.Boolean('Multi-base')
    retribution_rate = fields.Float('Retribution rate')
    quota_base_ids = fields.One2many('retribution.base.line', 'multi_base_id')


class RetributionBaseLine(models.Model):
    _name = 'retribution.base.line'
    _description = 'Retribution base Line'

    multi_base_id = fields.Many2one('retribution.base', string='Multi base')
    base_id = fields.Many2one('retribution.base', string='Base')
    volume = fields.Integer('Volume')
    volume_percentage = fields.Float('%vol')
    retribution_percentage = fields.Float('%retribution')
