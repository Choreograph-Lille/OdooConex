# -*- coding: utf-8 -*-
{
    'name': 'Choreograph SAGE',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'sequence': -97,
    'summary': 'Manage Choreograph SAGE',
    'description': """This module allows to install specific features on SAGE linking""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'choreograph_account',
        'purchase',
    ],
    'data': [
        # data
        # security
        'security/ir.model.access.csv',
        # views
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
        'views/account_tax_views.xml',
        'views/choreograph_sage_ftp_server_views.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
