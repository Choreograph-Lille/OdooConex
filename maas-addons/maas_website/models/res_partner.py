# -*- encoding: utf-8 -*-
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    operation_home_url = fields.Char('Operation Home URL', compute='_compute_operation_home_url', inverse='inverse_operation_home_url', store=True)

    @api.depends('commercial_partner_id', 'commercial_partner_id.operation_home_url', 'is_company', 'parent_id.commercial_partner_id')
    def _compute_operation_home_url(self):
        for rec in self:
            rec.operation_home_url = rec.commercial_partner_id.operation_home_url

    def inverse_operation_home_url(self):
        pass
