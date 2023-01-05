# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Accounting',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'sequence': -97,
    'summary': 'Manage Choreograph Accounting',
    'description': """This module allows to install specific features on accounting module""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'account',
        'l10n_fr',
        'choreograph_base',
    ],
    'data': [
        # data
        # security
        # views
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
