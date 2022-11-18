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

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_portal_user = fields.Boolean('Is Portal User', compute='_compute_portal_user')
    groups_id = fields.Many2many(default=False)
    bool_sms = fields.Boolean(string="SMS")
    bool_print = fields.Boolean(string="Print")
    bool_email = fields.Boolean(string="Email")
    default_sms = fields.Boolean(string="Default SMS")
    default_print = fields.Boolean(string="Default Print")
    default_email = fields.Boolean(string="Default Email")
    customer_ids = fields.Many2many('res.partner', 'res_users_customer_rel', 'user_id', 'partner_id', string='Customers',
                                    domain=[('customer_rank', '>', 0)])

    @api.onchange('default_sms')
    def onchange_default_sms(self):
        if self.default_sms:
            self.default_print = False
            self.default_email = False
            self.bool_sms = True

    @api.onchange('default_print')
    def onchange_default_print(self):
        if self.default_print:
            self.default_sms = False
            self.default_email = False
            self.bool_print = True

    @api.onchange('default_email')
    def onchange_default_email(self):
        if self.default_email:
            self.default_sms = False
            self.default_print = False
            self.bool_email = True

    @api.onchange('bool_sms')
    def onchange_bool_sms(self):
        if not self.bool_sms:
            self.default_sms = False

    @api.onchange('bool_print')
    def onchange_bool_print(self):
        if not self.bool_print:
            self.default_print = False

    @api.onchange('bool_email')
    def onchange_bool_email(self):
        if not self.bool_email:
            self.default_email = False

    def get_canal(self):
        self.ensure_one()
        result = []
        if self.bool_sms:
            result.append(('SMS', "1" if self.default_sms else "0"))
        if self.bool_print:
            result.append(('Print', "1" if self.default_print else "0"))
        if self.bool_email:
            result.append(('Email', "1" if self.default_email else "0"))
        return result

    def _password_has_expired(self):
        self.ensure_one()
        res = super(ResUsers,self)._password_has_expired()
        if self.company_id.groups_no_expiration:
            return res and not any(group_id in self.company_id.mapped('groups_no_expiration').ids
                               for group_id in self.mapped('groups_id').ids
                               )
        return res

    def _compute_portal_user(self):
        portal_users = self.env.ref('maas_base.standard_user').users
        portal_users |= self.env.ref('maas_base.validator_user').users
        for rec in self:
            if rec in portal_users:
                rec.is_portal_user = True
            else:
                rec.is_portal_user = False
