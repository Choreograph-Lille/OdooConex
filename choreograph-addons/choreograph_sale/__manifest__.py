# -*- coding: utf-8 -*-
{
    'name': 'choreograph sale',
    'summary': 'Manage choreograph sale',
    'sequence': 10,
    'description': "",
    'category': '',
    'website': '',
    'images': [],
    'depends': ['sale_project', 'project_template'],
    'data': [
        # views
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
