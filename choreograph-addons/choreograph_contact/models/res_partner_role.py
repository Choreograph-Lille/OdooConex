# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResPartnerRole(models.Model):
    _name = 'res.partner.role'
    _description = 'Partner Role'

    role_id = fields.Many2one('res.role', 'Role')
    user_ids = fields.Many2many('res.users', string='Users')
    partner_id = fields.Many2one('res.partner')

    @api.constrains('role_id', 'partner_id')
    def _check_unique_role(self):
        for record in self:
            if self.search_count([('role_id', '=', record.role_id.id), ('partner_id', '=', record.partner_id.id), ('id', '!=', record.id)]):
                raise ValidationError(_('The role %s is already set for this partner.') % record.role_id.name)
