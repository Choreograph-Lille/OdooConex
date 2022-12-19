# -*- encoding: utf-8 -*-

from odoo import models, api, fields


class IndicationIndication(models.Model):
    _name = 'indication.indication'
    _description = 'Indication Indication'

    name = fields.Char(string="Name", translate=True)
    image = fields.Binary(string="Image")
    default_sequence = fields.Integer(string="Default Sequence")
    partner_info_ids = fields.One2many('partner.indication.infos', 'indication_id', string="Infos",
                                       domain=['|', ('active', '=', False), ('active', '=', True)])


class PartnerIndicationInfos(models.Model):
    _name = 'partner.indication.infos'
    _description = 'Partner Indication Infos'

    partner_id = fields.Many2one('res.partner', string='Partner')
    quantity = fields.Integer(string='Quantity')
    indication_id = fields.Many2one('indication.indication', string='Indication')
    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Integer(string="Sequence")
