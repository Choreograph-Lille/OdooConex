# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Website',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Website',
    'sequence': -83,
    'summary': 'Manage Choreograph Website',
    'description': """This module allows to install specific website features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'website',
        'choreograph_base',
    ],
    'data': [
        # data
        # security
        # views
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
