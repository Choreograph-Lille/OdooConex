# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Sox',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Tools',
    'summary': 'Management of user rights, creation of user profiles',
    'sequence': -96,
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'sales_team',
        'project',
        'hr_expense',
        'documents',
        'base_user_role',
        'mass_mailing',
        'choreograph_purchase',
        'maas_base'
    ],
    'data': [
        # security
        'security/ir_rule.xml',
        'security/res_groups.xml',
        'security/ir_model_access.xml',
        # views
        'views/ir_ui_menu_views.xml',
        # data
        'data/studio_approval_rule.xml',
    ],
    'installable': True,
    'application': False,
}
