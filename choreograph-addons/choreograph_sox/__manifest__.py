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
        'purchase',
        'sales_team',
        'project',
        'hr_expense',
        'documents',
        'mass_mailing',
        'choreograph_base',
        'maas_base'
    ],
    'data': [
        'security/res_groups.xml'
    ],
    'installable': True,
    'application': False,
}
