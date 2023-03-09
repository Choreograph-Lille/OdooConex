# -*- coding: utf-8 -*-

from odoo import fields, models


class ChoreographCampaignDe(models.Model):
    _name = 'choreograph.campaign.de'
    _description = 'Choreograph Campign DE'

    name = fields.Char()
    description = fields.Char()
    active = fields.Boolean(default=True)
