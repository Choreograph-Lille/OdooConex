from odoo import models, fields, _

class SftpImportReport(models.Model):
    _name = "sftp.import.report"
    _description = "SAGE SFTP import report"
    _rec_name = "file_name"
    _order = "import_date desc"

    file_name = fields.Char(string="File name")
    import_date = fields.Datetime(
        string="Import date",
        default=fields.Datetime.now,
    )
    attachment_id = fields.Many2one(
        'ir.attachment',
        string="Imported file",
    )
    type = fields.Selection([
        ('sale', 'Sales'),
        ('purchase', 'Purchases'),
    ], string="File type")
    line_count = fields.Integer(string="Lines processed")
    success_count = fields.Integer(string="Success")
    error_count = fields.Integer(string="Errors")
    state = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial'),
        ('rejected', 'Rejected'),
        ('failed', 'Failed'),
    ], string="Status")
    duration = fields.Float(
        string="Duration (s)",
        digits=(10, 2),
    )
    message = fields.Text(string="Message")
    sftp_server_id = fields.Many2one(
        'choreograph.sage.sftp.server',
        string="SFTP Server",
    )
    error_line_ids = fields.One2many(
        'sftp.import.report.line',
        'report_id',
        string="Error details",
    )


class SftpImportReportLine(models.Model):
    _name = "sftp.import.report.line"
    _description = "SAGE SFTP import report line"

    report_id = fields.Many2one(
        'sftp.import.report',
        ondelete='cascade',
    )
    invoice_ref = fields.Char(string="Invoice reference")
    error_type = fields.Selection([
        ('file_invalid',      'Invalid file'),
        ('file_not_found',    'File not found'),
        ('unknown_status',    'Unknown status'),
        ('invoice_not_found', 'Invoice not found in Odoo'),
        ('wrong_state',       'Invoice not posted'),
        ('data_mismatch',     'Data mismatch'),
    ], string="Error type")
    message = fields.Text(string="Error cause")