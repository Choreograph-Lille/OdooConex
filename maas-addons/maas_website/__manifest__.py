# -*- encoding: utf-8 -*-
{
    'name': 'MAAS Website',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Website',
    'sequence': -95,
    'summary': 'MyModel As A Service Website',
    'description': """This module allows to manage operations of customer from FO""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'maas_crm',
        'maas_sale_subscription',
        'website',
    ],
    'data': [
        # data
        # security
        # views
        'views/menu.xml',
        'views/templates.xml',
        'views/assets.xml',
        'views/res_partner_views.xml',
    ],
    'assets': {
        'web.assets_tests': [],
        'web.assets_frontend': [],
    },
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
