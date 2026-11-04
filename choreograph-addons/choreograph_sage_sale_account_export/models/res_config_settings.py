# -*- coding: utf-8 -*-

from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sage_sale_export_file_prefix = fields.Char(
        string="File Prefix",
        config_parameter='choreograph_sage_sale_account_export.prefix'
    )
    sage_sale_export_file_suffix = fields.Char(
        string="File Suffix",
        config_parameter='choreograph_sage_sale_account_export.suffix'
    )
    sage_sale_sftp_export_server_id = fields.Many2one(
        'choreograph.sage.sftp.server',
        string="SFTP Server",
        config_parameter='choreograph_sage_sale_account_export.sftp_server_id'
    )
    sftp_ubl_export_server_id = fields.Many2one(
        comodel_name='choreograph.sage.sftp.server',
        string="UBL Export SFTP Server (ICD)",
        config_parameter='choreograph_sage_sale_account_export.sftp_ubl_server_id',
    )
