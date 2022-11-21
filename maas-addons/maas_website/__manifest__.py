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
    'name': 'Maas Website',
    'version': '1.0',
    'category': 'Website',
    'sequence': 5,
    'summary': '',

    "author": "Arkeup",
    "website": "www.arkeup.com",

    'depends': ['maas_crm', 'maas_sale', 'maas_sale_subscription', 'website', 'web', 'website_payment'],
    'description': """ This module allows to manage operations of customer from FO. """,
    'data': [
        # data
        # security
        # views
        'views/menu.xml',
        'views/templates.xml',
        'views/assets.xml',
        #'views/layout.xml',
    ],
    'assets': {
        'web.assets_tests': [

        ],
        'web.assets_frontend': [

        ],

    },
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
