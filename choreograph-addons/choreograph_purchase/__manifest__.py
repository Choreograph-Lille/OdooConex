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
        'choreograph_account',
    ],
    'data': [
        # data
        'data/mail_template_data.xml',
        # security
        "security/ir.model.access.csv",
        # views
        'views/account_move_views.xml',
        'views/account_move_wizard_views.xml',
        'views/purchase_order_views.xml',
        'views/res_partner_views.xml',
        # report
        'report/purchase_order_templates.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
