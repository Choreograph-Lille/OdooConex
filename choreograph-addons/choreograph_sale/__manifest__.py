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
    ],
    'data': [
        # data
        # security
        'security/ir.model.access.csv',
        # views
        'views/sale_order_views.xml',
        'views/operation_condition_views.xml',
        'views/product_template_views.xml',
        'views/retribution_base_views.xml',
        'views/ir_ui_menu_views.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
