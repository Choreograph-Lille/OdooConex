# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Purchase',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Purchase',
    'sequence': -89,
    'summary': 'Manage Choreograph Purchase',
    'description': """This module allows to install specific purchase features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'purchase',
        'web_studio',
        'choreograph_base',
        'choreograph_sox'
    ],
    'data': [
        'data/studio_approval_rule.xml',
        'views/purchase_order_views.xml'
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
