# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    role_ids = fields.One2many('res.partner.choreograph.role', 'partner_id', string='Roles')
