# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Sale',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Purchase',
    'sequence': -87,
    'summary': 'Manage Choreograph Sale',
    'description': """This module allows to install specific sale features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'sales_team',
        'project_template',
        'choreograph_contact',
        'choreograph_sale_project',
    ],
    'data': [
        # data
        # security
        'security/ir.model.access.csv',
        # views
        'views/sale_order.xml',
        'views/operation_condition.xml',
        'views/product_views.xml',
        'views/retribution_base_views.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
