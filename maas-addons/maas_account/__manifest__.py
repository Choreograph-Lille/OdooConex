# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Maas Accounting',
    'version': '1.0',
    'category': 'Accounting',
    'sequence': 2,
    'summary': '',
    
    "author": "Arkeup",
    "website": "www.arkeup.com",    
    
    
    'depends': ['account', 'maas_base', 'l10n_fr'],
    'description': """ """,
    'data': [
        # data
        # security
        # views   
        'views/account_move_views.xml'
        # report
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
