# -*- encoding: utf-8 -*-

from odoo import models, fields


class PartnerIndicationInfos(models.Model):
    _name = 'partner.indication.infos'
    _description = 'Partner Indication Infos'

    partner_id = fields.Many2one('res.partner', string='Partner')
    quantity = fields.Integer()
    indication_id = fields.Many2one('indication.indication', string='Indication')
    active = fields.Boolean(default=True)
    sequence = fields.Integer()
