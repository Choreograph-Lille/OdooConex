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
        'account',
        'maas_base',
        'l10n_fr'
    ],
    'data': [
        # data
        # security
        # views   
        'views/account_move_views.xml'
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
