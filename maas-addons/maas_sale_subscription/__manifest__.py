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
    'name': 'Maas Sale Subscription',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 5,
    'summary': '',

    "author": "Arkeup",
    "website": "www.arkeup.com",

    'depends': ['maas_sale', 'sale_subscription'],
    'description': """ """,

    'data': [
        # data
        #'data/sale_subscription_template_data.xml',
        'data/product_template_data.xml',
        'data/ir_cron.xml',
        # security
        'security/ir.model.access.csv',
        # views
        'views/menu.xml',
        'views/sale_subscription_view.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
