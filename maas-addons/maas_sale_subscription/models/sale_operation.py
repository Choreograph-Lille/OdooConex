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
from odoo import _, api, fields, models


class SaleOperation(models.Model):
    _inherit = 'sale.operation'

    balance = fields.Integer(compute='compute_balance', store=True)

    @api.depends('partner_id', 'partner_id.subscription_ids', 'partner_id.subscription_ids.state', 'partner_id.subscription_ids.balance')
    def compute_balance(self):
        for rec in self:
            balance = 0
            if not rec.partner_id:
                balance = 0
            else:
                subscription = rec.partner_id.get_active_subscription()
                if subscription:
                    balance = subscription.balance
            rec.balance = balance

    def check_quantity(self):
        self.ensure_one()
        result = super(SaleOperation, self).check_quantity()
        if self.balance < 0:
            raise ValidationError(_('The balance is not enough.'))
        return result
