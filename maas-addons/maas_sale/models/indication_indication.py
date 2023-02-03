# -*- encoding: utf-8 -*-

from odoo import models, fields


class IndicationIndication(models.Model):
    _name = 'indication.indication'
    _description = 'Indication Indication'

    name = fields.Char(translate=True)
    image = fields.Binary()
    default_sequence = fields.Integer()
    partner_info_ids = fields.One2many('partner.indication.infos', 'indication_id', string="Infos",
                                       domain=['|', ('active', '=', False), ('active', '=', True)])



