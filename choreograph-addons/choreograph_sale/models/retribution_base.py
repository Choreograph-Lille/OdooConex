# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError


class RetributionBase(models.Model):
    _name = 'retribution.base'
    _description = 'Retribution base'

    name = fields.Char('Name', required=True)
    is_open = fields.Boolean('Open')
    is_multi_base = fields.Boolean('Multi-bases')
    retribution_rate = fields.Float('Retribution rate')
    quota_base_ids = fields.One2many('retribution.base.line', 'multi_base_id')

    @api.onchange('quota_base_ids', 'is_multi_base')
    def _compute_retribution_rate(self):
        for rec in self:
            if rec.is_multi_base:
                rec.retribution_rate = sum([qb.volume_percentage * qb.retribution_percentage for qb in rec.quota_base_ids])/100
            else:
                rec.retribution_rate = 0

    def write(self, vals):
        result = super(RetributionBase, self).write(vals)
        for rec in self:
            total_volume = round(sum(rec.quota_base_ids.mapped('volume_percentage')))
            if total_volume != 100 and rec.is_multi_base:
                raise ValidationError(_('Volume percentage is {0}%, this should be at 100%').format(total_volume))
            return result


class RetributionBaseLine(models.Model):
    _name = 'retribution.base.line'
    _description = 'Retribution base Line'

    multi_base_id = fields.Many2one('retribution.base', string='Multi base')
    base_id = fields.Many2one('retribution.base', string='Base')
    volume = fields.Integer('Volume')
    volume_percentage = fields.Float('%vol')
    retribution_percentage = fields.Float('%retribution')
