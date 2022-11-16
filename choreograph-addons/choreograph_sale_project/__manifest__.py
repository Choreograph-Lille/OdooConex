# -*- coding: utf-8 -*-
{
    'name': 'choreograph sale project',
    'summary': 'Manage relation between choreograph sale and project',
    'sequence': 10,
    'description': "",
    'category': '',
    'website': '',
    'images': [],
    'depends': ['sale_project'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/project_views.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
    'application': False,
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
}
