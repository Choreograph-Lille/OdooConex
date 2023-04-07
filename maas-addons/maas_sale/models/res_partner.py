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

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type = fields.Selection([('alliance', 'Alliance'), ('conexplus', 'Conex +')],
                                    default='alliance', tracking=10)
    title_ref = fields.Char('Title Ref.', size=6, tracking=10)
    operation_ids = fields.One2many('sale.operation', 'partner_id', 'Operations')
    campaign_ids = fields.One2many('sale.campaign', 'partner_id', 'Campaigns')
    subscription_ids = fields.One2many('sale.order', 'partner_id', 'Subscriptions ')
    date_update_title = fields.Date(tracking=10)
    date_update_vars = fields.Date(tracking=10)

    def get_active_subscription(self):
        self.ensure_one()
        order_obj = self.env['sale.order']
        partner = self.get_parent()
        order = order_obj.search([('partner_id', '=', partner.id),
                                   ('is_subscription', '=', True),
                                   ('state', 'in', ('sale', 'done')),
                                   ('stage_id.category', '=', 'progress')], limit=1)

        if not order:
            return False
        return order
