# -*- coding: utf-8 -*-
{
    'name': 'MAAS APP',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Application',
    'sequence': -100,
    'summary': 'MyModel As A Service Application',
    'description': """This module allows to install all MAAS environment""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'maas_sale_subscription',
        'maas_website',
        'maas_account'
    ],
    'data': [
        # data
        # security
        # views
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': True,
}
