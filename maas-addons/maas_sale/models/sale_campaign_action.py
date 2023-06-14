# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 ArkeUp (<http://www.arkeup.fr>). All Rights Reserved
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

from odoo import api, fields, models


class SaleCampaignAction(models.Model):
    _name = 'sale.campaign.action'
    _description = 'Sale Campaign Action'

    name = fields.Char(required=True)
    partner_id = fields.Many2one(related='campaign_id.partner_id', readonly=True)
    campaign_id = fields.Many2one('sale.campaign', 'Sale Campaign', required=True, ondelete='cascade')
    operation_ids = fields.One2many('sale.operation', 'action_id', 'Operations', readonly=True)
    has_archived = fields.Boolean(compute='has_operation_archived')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('filtered_by_campaign'):
            args += [('campaign_id', '=', self._context.get('filtered_by_campaign'))]
        return super(SaleCampaignAction, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                       access_rights_uid=access_rights_uid)

    @api.depends('operation_ids')
    def has_operation_archived(self):
        for act in self:
            if len(act.operation_ids.filtered(lambda j: j.archived)):
                act.has_archived = True
            else:
                act.has_archived = False
