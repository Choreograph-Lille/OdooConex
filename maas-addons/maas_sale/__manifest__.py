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

{
    'name': 'Maas Sale',
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'Sales',
    'sequence': 4,
    'summary': '',

    "author": "Arkeup",
    "website": "www.arkeup.com",

    'depends': [
        'sale',
        'maas_base'
    ],
    'description': """ """,
    'data': [
        # data
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'data/ir_config_parameter.xml',
        'data/ir_cron.xml',
        # security
        'security/ir.model.access.csv',
        # 'security/user_groups.xml',
        # views
        'views/sale_action.xml',
        'views/sale_campaign.xml',
        'views/res_partner_view.xml',
        'views/sale_operation_view.xml',
        'views/package_upgrade.xml',
        'views/menu.xml',
        'views/product_pricelist_views.xml',
        'views/res_config_settings.xml',
        'views/indication_views.xml',
        # report
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
