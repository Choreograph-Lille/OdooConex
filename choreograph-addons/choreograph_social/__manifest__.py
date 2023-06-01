# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Social',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Tools',
    'summary': 'Manage Choreograph Social',
    'sequence': -85,
    'description': """This module allows to install Choreograph Social Features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'choreograph_base',
        'mail_optional_follower_notification',
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
