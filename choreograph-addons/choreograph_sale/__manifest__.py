# -*- coding: utf-8 -*-
{
    'name': 'choreograph sale',
    'summary': 'Manage choreograph sale',
    'sequence': 10,
    'description': "",
    'category': '',
    'website': '',
    'images': [],
    'depends': ['choreograph_sale_project', 'project_template', 'choreograph_contact'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/sale_order.xml',
        'views/operation_condition.xml',
        'views/sale_base_views.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
}
