# -*- coding: utf-8 -*-
{
    'name': 'Choreograph SAGE SFTP Import',
    'version': '16.0.0.0',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'sequence': -98,
    'summary': 'Manage Choreograph SAGE In invoice import',
    'description': """This module allows to import invoice from sage""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'choreograph_sage_sftp_server',
        'choreograph_account',
        'account'
    ],
    'data': [
        'views/res_config_settings_views.xml'
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
