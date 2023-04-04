# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RetributionBase(models.Model):
    _name = 'retribution.base'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'Retribution base'

    name = fields.Char(required=True, tracking=True)
    is_open = fields.Boolean('Open', tracking=True)
    is_multi_base = fields.Boolean('Multi-Bases', tracking=True)
    retribution_rate = fields.Float(tracking=True, compute='_compute_retribution_rate', store=True, readonly=False)
    quota_base_ids = fields.One2many('retribution.base.line', 'multi_base_id', 'Quotas', tracking=True)
    postal_variable = fields.Float('Postal Variable', tracking=True, default=0.3)
    postal_address = fields.Float('Postal address', tracking=True, default=1.0)
    product_template_id = fields.Many2one('product.template', 'Product')
    code = fields.Char('Code')

    @api.onchange('quota_base_ids', 'is_multi_base')
    def _onchange_quota_base(self):
        if self.is_multi_base:
            total_volume = sum(self.quota_base_ids.mapped('volume'))
            for qb in self.quota_base_ids:
                qb.volume_percentage = (qb.volume / total_volume) * 100 if total_volume else 0

    @api.depends('quota_base_ids')
    def _compute_retribution_rate(self):
        for rec in self:
            if rec.is_multi_base:
                rec.retribution_rate = sum(
                    [qb.volume_percentage * qb.retribution_percentage for qb in rec.quota_base_ids]) / 100
            else:
                rec.retribution_rate = rec.retribution_rate

    def write(self, vals):
        res = super(RetributionBase, self).write(vals)
        self._check_volume_percent()
        return res

    def _check_volume_percent(self):
        for record in self:
            total_volume = round(sum(record.quota_base_ids.mapped('volume_percentage')))
            if total_volume != 100 and record.is_multi_base:
                raise ValidationError(_('Volume percentage is {0}%, this should be at 100%').format(total_volume))
