# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class SftpExportReport(models.Model):
    _name = "sftp.export.report"
    _description = "SFTP Export Report"
    _rec_name = "file_name"
    _order = "export_date desc"

    file_name = fields.Char(string="File Name")
    export_date = fields.Datetime(
        default=fields.Datetime.now,
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Exported File",
    )
    type = fields.Selection(
        [
            ("invoice_collected", "Invoice Collected"),
        ],
        string="Export Type",
    )
    line_count = fields.Integer(string="Lines Processed")
    success_count = fields.Integer(string="Success")
    error_count = fields.Integer(string="Errors")
    state = fields.Selection(
        [
            ("success", "Success"),
            ("partial", "Partial"),
            ("rejected", "Rejected"),
            ("failed", "Failed"),
        ],
        string="Status",
    )
    message = fields.Text(string="Message")
    sftp_server_id = fields.Many2one(
        "choreograph.sage.sftp.server",
        string="SFTP Server",
    )
    line_ids = fields.One2many(
        "sftp.export.report.line",
        "report_id",
        string="Export Details",
    )


class SftpExportReportLine(models.Model):
    _name = "sftp.export.report.line"
    _description = "SFTP Export Report Line"

    report_id = fields.Many2one(
        "sftp.export.report",
        ondelete="cascade",
    )
    invoice_ref = fields.Char(string="Invoice Reference")
    amount_total = fields.Float(string="Amount TTC")
    status = fields.Char(string="Status")

    @api.model
    def create(self, vals):
        result = super().create(vals)
        report = result.report_id
        log_message = (
            f"{report.export_date.strftime('%d/%m/%Y %H:%M:%S')} - "
            f"{report.type} - {report.file_name} - "
            f"{result.invoice_ref} - {report.line_count} - {result.status}"
        )
        _logger.info(log_message)
        return result
