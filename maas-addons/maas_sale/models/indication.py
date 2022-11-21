# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2022 ArkeUp (<http://www.arkeup.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, api, fields


class IndicationIndication(models.Model):
    _name = 'indication.indication'

    name = fields.Char(string="Name", translate=True)
    image = fields.Binary(string="Image")
    default_sequence = fields.Integer(string="Default Sequence")
    partner_info_ids = fields.One2many('partner.indication.infos', 'indication_id', string="Infos",
                                       domain=['|', ('active', '=', False), ('active', '=', True)])


class PartnerIndicationInfos(models.Model):
    _name = 'partner.indication.infos'

    partner_id = fields.Many2one('res.partner', string='Partner')
    quantity = fields.Integer(string='Quantity')
    indication_id = fields.Many2one('indication.indication', string='Indication')
    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Integer(string="Sequence")
