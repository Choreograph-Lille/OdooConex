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

from odoo.exceptions import ValidationError
from odoo import fields, models, api, _


class SaleCampaign(models.Model):
    _name = 'sale.campaign'
    _description = 'Sale Campaign'

    @api.model
    def default_get(self, fields):
        res = super(SaleCampaign, self).default_get(fields)
        if not res.get('partner_id'):
            res['partner_id'] = self.env.user.partner_id.id
        return res

    name = fields.Char(required=True)
    partner_id = fields.Many2one('res.partner', 'Customer', ondelete='cascade')
    action_ids = fields.One2many('sale.campaign.action', 'campaign_id', 'Actions', readonly=True)
    operation_ids = fields.One2many('sale.operation', 'campaign_id', 'Operations', readonly=True)
    has_archived = fields.Boolean(compute='has_operation_archived')

    @api.constrains('operation_ids', 'partner_id')
    def _check_operation_of_partner(self):
        for campaign in self:
            if campaign.partner_id and campaign.operation_ids:
                if len(campaign.operation_ids.mapped('partner_id')) > 1 or campaign.operation_ids.mapped('partner_id') not in \
                        campaign.partner_id:
                    raise ValidationError(_('Campaign must contain only operations of the defined customer.'))

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        """ Override that adds specific filtering by partner. """
        if self._context.get('filtered_by_partner'):
            args += [('partner_id', '=', self._context.get('filtered_by_partner'))]
        return super(SaleCampaign, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                 access_rights_uid=access_rights_uid)

    @api.depends('operation_ids')
    def has_operation_archived(self):
        for sub in self:
            if len(sub.operation_ids.filtered(lambda j: j.archived)):
                sub.has_archived = True
            else:
                sub.has_archived = False
