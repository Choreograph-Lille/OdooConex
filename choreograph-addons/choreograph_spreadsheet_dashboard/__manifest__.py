# -*- coding: utf-8 -*-
{
    "name": "Choreograph Spreadsheet Dashboard",
    "version": "16.0.0.1",
    "license": "LGPL-3",
    "category": "Dashboard",
    "summary": "Manage Choreograph Spreadsheet Dashboard",
    "sequence": -90,
    "description": """This module allows to install Choreograph"s Spreadsheet Dashboard specifications""",
    "author": "ArkeUp",
    "website": "https://arkeup.com",
    "depends": [
        "spreadsheet_dashboard",
        "choreograph_base",
    ],
    "data": [
        # data
        # security
        "security/ir.model.access.csv",
        "security/ir_model_access.xml",
        # views
    ],
    "assets": {
        "web._assets_primary_variables": [],
        "web.assets_backend": [],
        "web.assets_frontend": [],
    },
    "installable": True,
    "application": False,
}
