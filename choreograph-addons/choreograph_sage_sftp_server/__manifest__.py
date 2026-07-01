# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Sage SFTP Server',
    'version': '16.0.0.1',
    'summary': 'Manage connection between Sage → Odoo via SFTP',
    'category': 'Accounting',
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/choreograph_sage_sftp_server_views.xml',
        'views/sftp_logging_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
