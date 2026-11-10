# -*- coding: utf-8 -*-

from odoo import fields, models


class SftpExportReport(models.Model):
    _inherit = "sftp.export.report"

    type = fields.Selection(
        selection_add=[("ereporting_supplier", "E-Reporting Suppliers")],
        ondelete={"ereporting_supplier": "set null"},
    )
    exported_move_names = fields.Text(string="Exported Documents")
