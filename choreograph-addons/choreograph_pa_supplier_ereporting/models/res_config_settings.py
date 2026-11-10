# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    pa_ereporting_remote_path = fields.Char(
        string="E-Reporting Directory",
        config_parameter="choreograph_pa_supplier_ereporting.remote_path",
        help="Directory of the PA ICD SFTP server where the E-Reporting file is sent "
             "(default: ereporting).",
    )
