# -*- coding: utf-8 -*-
{
    'name': 'Choreograph Auditlog',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Tools',
    'summary': 'Auditlog customization',
    'sequence': -96,
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'auditlog'
    ],
    'data': [
        'security/ir.model.access.csv',

        'report/layout.xml',
        'report/user_roles_and_right_template.xml',
        'report/sox_role_permissions_template.xml',
        'report/auditlog_log_template.xml',
        'report/closing_purchase_template.xml',
        'report/supplier_bank_details_template.xml',
        'report/account_template.xml',
        'report/quote_purchase_order_template.xml',
        'report/auditlog_report_wizard.xml',

        'data/auditlog_rule.xml',

        'wizards/auditlog_report_wizard.xml',
    ],
    'installable': True,
    'application': False,
}
