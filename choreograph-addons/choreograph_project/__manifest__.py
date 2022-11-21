# -*- coding: utf-8 -*-
{
    'name': 'choreograph project',
    'summary': 'Manage choreograph project',
    'sequence': 10,
    'description': "",
    'category': '',
    'website': '',
    'images': [],
    'depends': ['choreograph_contact', 'choreograph_sale_project', 'choreograph_sale'],
    'data': [
        # security
        # 'security/ir.model.access.csv',
        # views
        'views/project_views.xml',
    ],
    'installable': True,
    'application': False,
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
}
