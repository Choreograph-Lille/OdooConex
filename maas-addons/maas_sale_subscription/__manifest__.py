# -*- encoding: utf-8 -*-

{
    'name': 'Maas Sale Subscription',
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'Sales',
    'sequence': 5,
    'summary': '',

    "author": "Arkeup",
    "website": "www.arkeup.com",

    'depends': [
        'maas_sale',
        'sale_subscription'
    ],
    'description': """ """,

    'data': [
        # data
        'data/product_template_data.xml',
        'data/ir_cron.xml',
        'data/ir_config_parameter_data.xml',
        # security
        'security/ir_rule.xml',
        'security/ir.model.access.csv',
        # views
        'views/menu.xml',
        'views/product_template_view.xml',
        'views/sale_order_view.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
