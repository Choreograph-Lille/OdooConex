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

from dateutil import tz

from odoo import api, fields, models


class SaleOperation(models.Model):
    _inherit = 'sale.operation'

    @api.model
    def _get_date_tz(self, value=False):
        if not value:
            return False
        from_tz = tz.tzutc()
        to_tz = tz.gettz(self.env.user.tz)
        datetime_wo_tz = fields.Datetime.from_string(value)
        datetime_with_tz = datetime_wo_tz.replace(tzinfo=from_tz)
        return fields.Datetime.to_string(datetime_with_tz.astimezone(to_tz))
