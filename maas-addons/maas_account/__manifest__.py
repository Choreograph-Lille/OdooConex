# -*- coding: utf-8 -*-
{
    'name': 'MAAS Accounting',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'sequence': -99,
    'summary': 'MyModel As A Service Application',
    'description': """This module allows to install specific features on accounting module""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'l10n_fr',
        'account',
        'maas_base',
    ],
    'data': [
        # data
        # security
        # views
        'views/res_partner_views.xml',
        'views/account_move_views.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
