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
    'name': 'Maas Base',
    'version': '1.0',
    'category': '',
    'sequence': 1,
    'summary': '',
    
    "author": "Arkeup",
    "website": "www.arkeup.com",
    
    
    'depends': ['mail', 'sale', 'product', 'contacts'],

    'description': """ """,
    'data': [
        # data
        'data/res_company.xml',
        'data/res_partner.xml',
        'data/res_users_data.xml',
        'data/mail_templates.xml',
        # security
        'security/user_groups.xml',
        'security/user_profiles.xml',
        'security/ir.model.access.csv',
        # views
        'views/mail_message.xml',
        'views/res_users_view.xml',
        'views/res_partner_view.xml',
        'views/templates.xml',
        # report
        'report/template.xml',
    ],
    'update_xml': [],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
