# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError


class RetributionBase(models.Model):
    _name = 'retribution.base'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Retribution base'

    name = fields.Char(required=True, tracking=True)
    is_open = fields.Boolean('Open', tracking=True)
    is_multi_base = fields.Boolean('Multi-Bases', tracking=True)
    retribution_rate = fields.Float('Retribution Rate', tracking=True)
    quota_base_ids = fields.One2many('retribution.base.line', 'multi_base_id', 'Quotas', tracking=True)

    @api.onchange('quota_base_ids', 'is_multi_base')
    def _onchange_quota_base(self):
        self.retribution_rate = 0
        if self.is_multi_base:
            self.retribution_rate = sum([qb.volume_percentage * qb.retribution_percentage for qb in self.quota_base_ids]) / 100

    def write(self, vals):
        res = super(RetributionBase, self).write(vals)
        self._check_volume_percent()
        return res

    def _check_volume_percent(self):
        for record in self:
            total_volume = round(sum(record.quota_base_ids.mapped('volume_percentage')))
            if total_volume != 100 and record.is_multi_base:
                raise ValidationError(_('Volume percentage is {0}%, this should be at 100%').format(total_volume))
