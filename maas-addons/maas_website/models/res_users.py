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


class ResUsers(models.Model):
    _inherit = 'res.users'

    portal_filter = fields.Selection([('all-operations', 'All operations'),
                                      ('last-30-days', 'Last 30 days'),
                                      ('last-3-months', 'Last 3 months'),
                                      ('last-6-months', 'Last 6 months'),
                                      ('last-12-months', 'Last 12 months'),
                                      ('trimester-1', 'Trimester 1'),
                                      ('trimester-2', 'Trimester 2'),
                                      ('trimester-3', 'Trimester 3'),
                                      ('trimester-4', 'Trimester 3')])

    def is_standard(self):
        self.ensure_one()
        if self in self.env.ref('maas_base.standard_user_role').users:
            return True
        return False

    def is_validator(self):
        self.ensure_one()
        if self in self.env.ref('maas_base.validator_user_role').users:
            return True
        return False
