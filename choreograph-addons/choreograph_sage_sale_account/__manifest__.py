{
    'name': 'Choreograph SAGE Sale Account',
    'version': '16.0.0.0',
    'license': 'LGPL-3',
    'category': 'Accounting',
    'sequence': -97,
    'summary': 'Manage Choreograph SAGE Out invoice import',
    'description': "This module allows to import sale invoice payments from Sage",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'choreograph_sage_sftp_server',
        'choreograph_account',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_cron_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
}