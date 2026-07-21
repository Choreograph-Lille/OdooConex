# -*- coding: utf-8 -*-
{
    "name": "Choreograph SAGE Sale Account Export",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "category": "Accounting",
    "sequence": -97,
    "summary": "Manage Choreograph SAGE Sale invoice export to PA ICD",
    "description": """This module allows to export paid sale invoices to PA ICD""",
    "author": "ArkeUp",
    "website": "https://arkeup.com",
    "depends": [
        "choreograph_sage",
        "choreograph_sage_sftp_server",
        "choreograph_sage_sale_account",
        "choreograph_account",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "views/res_config_settings_views.xml",
        "views/account_move_views.xml",
        "views/sftp_export_report_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
