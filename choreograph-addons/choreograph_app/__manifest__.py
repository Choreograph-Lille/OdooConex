# -*- coding: utf-8 -*-
{
    'name': 'Choreograph APP',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Tools',
    'summary': 'Manage Choreograph Environment',
    'sequence': -96,
    'description': """This module allows to install Choreograph's applications""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'choreograph_hr',
        'choreograph_sox',
        'choreograph_i18n',
        'choreograph_mail',
        'choreograph_social',
        'choreograph_website',
        'choreograph_auditlog',
        'choreograph_sale_project',
        'choreograph_sale_discount',
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
    'application': True,
}
