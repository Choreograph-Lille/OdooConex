# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    concerned_base = fields.Many2one('retribution.base', string='Concerned base')
    datastore = fields.Boolean('Datastore')
    retribution_rate = fields.Float('Retribution rate')

    @api.depends_context('company')
    @api.depends('retribution_rate')
    def _compute_standard_price(self):
        for rec in self:
            rec.standard_price = (rec.retribution_rate * rec.list_price) / 100
