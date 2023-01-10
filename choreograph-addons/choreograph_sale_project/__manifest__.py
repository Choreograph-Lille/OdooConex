# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Sale Project',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Sales',
    'sequence': -85,
    'summary': 'Manage Sale Project',
    'description': """This module allows to manage the relation between sale and project""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'sale_project',
        'choreograph_sale',
        'choreograph_project',
    ],
    'data': [
        # data
        # security
        'security/ir.model.access.csv',
        # views
        'views/project_views.xml',
        'views/sale_order.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
