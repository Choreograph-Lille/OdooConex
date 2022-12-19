# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Contact',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Contact',
    'summary': 'Manage choreograph contacts',
    'sequence': -96,
    'description': """This module allows to install specific contact features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'contacts',
        'choreograph_account',
        'choreograph_purchase',
        'choreograph_sale',
    ],
    'data': [
        # data
        # security
        'security/ir.model.access.csv',
        # views
        'views/choreograph_role_views.xml',
        'views/res_partner_views.xml',
    ],

    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
