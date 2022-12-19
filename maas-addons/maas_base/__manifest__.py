# -*- encoding: utf-8 -*-
{
    'name': 'MAAS Base',
    'version': '16.0.0.1',
    'category': 'Tools',
    'sequence': -98,
    'summary': 'MyModel As A Service Base Module',
    'description': """This module allows to install base features will be used by all other modules""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'mail',
        'sale',
        'product',
        'contacts'
    ],
    'data': [
        # data
        'data/res_company.xml',
        'data/res_partner.xml',
        'data/res_users_data.xml',
        'data/mail_templates.xml',
        # security
        'security/user_groups.xml',
        'security/user_profiles.xml',
        'security/ir.model.access.csv',
        # views
        'views/mail_message.xml',
        'views/res_users_view.xml',
        'views/res_partner_view.xml',
        'views/templates.xml',
        # report
        'report/template.xml',
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
