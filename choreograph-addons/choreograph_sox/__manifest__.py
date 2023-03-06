# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Sox : User rights management',
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
        'security/res_groups.xml',
        'data/studio_approval_rule.xml',
    ],
    'installable': True,
    'application': False,
}
