# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class RetributionBase(models.Model):
    _name = 'retribution.base'
    _description = 'Retribution base'

    name = fields.Char('Name', required=True)
    is_open = fields.Boolean('Open')
    is_multi_base = fields.Boolean('Multi-base')
    retribution_rate = fields.Float('Retribution rate', compute='_compute_retribution_rate')
    quota_base_ids = fields.One2many('retribution.base.line', 'multi_base_id')

    @api.depends('quota_base_ids', 'is_multi_base')
    def _compute_retribution_rate(self):
        for rec in self:
            if rec.is_multi_base:
                rec.retribution_rate = sum([qb.volume_percentage * qb.retribution_percentage for qb in rec.quota_base_ids])/100
            else:
                rec.retribution_rate = 0


class RetributionBaseLine(models.Model):
    _name = 'retribution.base.line'

    multi_base_id = fields.Many2one('retribution.base', string='Multi base')
    base_id = fields.Many2one('retribution.base', string='Base')
    volume = fields.Integer('Volume')
    volume_percentage = fields.Float('%vol')
    retribution_percentage = fields.Float('%retribution')
