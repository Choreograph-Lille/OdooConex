# -*- coding: utf-8 -*-
{
    'name': 'choreograph contact',
    'summary': 'Manage choreograph contacts',
    'sequence': 10,
    'description': "",
    'category': '',
    'website': '',
    'images': [],
    'depends': ['base', 'contacts', 'account', 'purchase', 'l10n_fr'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/choreograph_role_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
}
