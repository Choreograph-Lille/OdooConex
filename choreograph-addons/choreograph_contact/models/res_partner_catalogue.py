# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartnerCatalogue(models.Model):
    _name = 'res.partner.catalogue'
    _description = 'Partner Catalogue'

    name = fields.Char('Name')
    color = fields.Integer('Color', default=1)
    active = fields.Boolean(default=True)
