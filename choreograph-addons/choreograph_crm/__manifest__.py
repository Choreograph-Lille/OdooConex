# -*- coding: utf-8 -*-
{
    'name': 'Choreograph CRM',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'CRM',
    'sequence': -94,
    'summary': 'Manage Choreograph CRM',
    'description': """This module allows to install CRM specific features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'sale_crm',
        'choreograph_contact'
    ],
    'data': [
        # data
        # security
        # views
        'views/crm_lead_views.xml',
    ],
    'installable': True,
    'application': False,
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
}
