# -*- coding: utf-8 -*-
{
    "name": "Choreograph PA Supplier E-Reporting",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "category": "Accounting",
    "summary": "Weekly export of supplier invoices and credit notes outside the reform to the PA ICD",
    "description": """Every Monday, the module sends the posted supplier invoices and credit notes
of B2C / B2BINT vendors to the PA ICD SFTP (E-Reporting), then marks them as transferred.""",
    "author": "ArkeUp",
    "website": "https://arkeup.com",
    "depends": [
        "account_tax_unece",
        "choreograph_account",
        "choreograph_sage",
        "choreograph_sage_sale_account_export",
    ],
    "data": [
        "data/ir_cron_data.xml",
        "views/account_move_views.xml",
        "views/sftp_export_report_views.xml",
        "views/res_config_settings_views.xml",
        "views/menus.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
}
