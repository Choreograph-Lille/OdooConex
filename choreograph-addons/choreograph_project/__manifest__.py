# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Project',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'CRM',
    'sequence': -90,
    'summary': 'Manage Choreograph Project',
    'description': """This module allows to install specific project features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'choreograph_contact',
    ],
    'data': [
        # data
        'data/project_project_stage.xml',
        'data/project_task_type.xml',
        # report
        'report/project_report.xml',
        # views
        'views/project_views.xml',
        'views/project_update.xml',
        'views/project_task_type.xml',
        'views/ir_actions_act_windows.xml',
        'views/ir_ui_menu.xml'
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [
            'choreograph_project/static/src/**/*',
        ],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
