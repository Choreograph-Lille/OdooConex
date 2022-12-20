# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ChoreographRole(models.Model):
    _name = 'choreograph.role'
    _description = 'Role'

    name = fields.Char()


class ResPartnerChoreographRole(models.Model):
    _name = 'res.partner.choreograph.role'
    _description = 'Partner Role'

    role_id = fields.Many2one('choreograph.role', string='Role')
    user_ids = fields.Many2many('res.users', string='Users')
    partner_id = fields.Many2one('res.partner')

    _sql_constraints = [
        ('unique_role_partner', 'unique (role_id, partner_id)', _('This role is already set for this client.'))
    ]
