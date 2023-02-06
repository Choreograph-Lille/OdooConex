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


class MailMessage(models.Model):
    _inherit = 'mail.message'

    message_body = fields.Html()
    stage = fields.Selection([('stage_01', 'Stage 01'), ('stage_02', 'Stage 02')], default='stage_01')

    def create_message(self, data):
        message = ""
        if data:
            message = "&bull;  %s: %s &rarr; %s" % (
                data.get('changed_field', ''), data.get('old_value', ''), data.get('new_value', ''))
        return message

    def message_format(self, format_reply=True):
        for rec in self:
            res_ = super(MailMessage, rec).message_format()
            if res_ and res_[0].get('tracking_value_ids'):
                if res_[0]['model'] in ['sale.operation', 'sale.operation.child']:
                    rec.message_body = rec.create_message(res_[0]['tracking_value_ids'][0])
        return super(MailMessage, self).message_format(format_reply)

    def create(self, vals):
        if isinstance(vals, dict) and vals.get('model') in ['sale.operation', 'sale.operation.child']:
            vals.update({'stage': self._context.get('stage', 'stage_01')})
        if isinstance(vals, list):
            for val in vals:
                if val.get('model') in ['sale.operation', 'sale.operatoin.child']:
                    val.update({'stage': self._context.get('stage', 'stage_01')})
        return super(MailMessage, self).create(vals)
