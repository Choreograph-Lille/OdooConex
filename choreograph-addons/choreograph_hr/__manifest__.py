# -*- coding: utf-8 -*-
{
    'name': 'Choreograph HR',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'HR',
    'sequence': -93,
    'summary': 'Manage Choreograph Human Resources',
    'description': """This module allows to install specific Human Resources features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'hr',
        'hr_contract',
        'choreograph_base'
    ],
    'data': [
        # data
        # security
        # views
        'views/hr_employee.xml'
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
