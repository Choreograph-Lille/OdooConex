# -*- coding: utf-8 -*-

{
    'name': 'Choreograph Sale',
    'version': '16.0.0.1',
    'license': 'LGPL-3',
    'category': 'Purchase',
    'sequence': -87,
    'summary': 'Manage Choreograph Sale',
    'description': """This module allows to install specific sale features""",
    'author': 'ArkeUp',
    'website': 'https://arkeup.com',
    'depends': [
        'sales_team',
        'project_template',
        'choreograph_contact',
        'sale_purchase',
        'hr_holidays',
    ],
    'data': [
        # data
        'data/sale_data_conservation_data.xml',
        'data/mail_template_data.xml',
        'data/ir_cron_data.xml',
        # security
        'security/ir.model.access.csv',
        # wizards
        'wizards/operation_generation_views.xml',
        # report
        'report/report_terms_templates.xml',
        'report/report_templates.xml',
        # views
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/operation_condition_views.xml',
        'views/product_template_views.xml',
        'views/retribution_base_views.xml',
        'views/sale_data_conservation_views.xml',
        'views/choreograph_campaign_de.xml',
        'views/res_company_views.xml',
        'views/res_config_settings_views.xml',
        'views/sale_portal_templates.xml',
        'views/ir_ui_menu_views.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [],
        'web.assets_backend': [],
        'web.assets_frontend': [],
    },
    'installable': True,
    'application': False,
}
