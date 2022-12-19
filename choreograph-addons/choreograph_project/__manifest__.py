# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Project',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'CRM',
    'sequence': -90,
    'summary': 'Manage Choreograph Project',
    'description': """This module allows to install specific project features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'choreograph_sale',
        'choreograph_contact',
        'choreograph_sale_project'],
    'data': [
        # security
        # 'security
        # views
        'views/project_views.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
