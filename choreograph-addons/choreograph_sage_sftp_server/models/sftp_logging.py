from odoo import models, fields

class SftpLogging(models.Model):
    _name = "sftp.logging"
    _description = "SAGE SFTP import log"
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
        ('customer', 'Sales'),                 
        ('supplier', 'Purchases'),                 
    ], string="File type")
    line_count = fields.Integer(string="Lines processed")
    success_count = fields.Integer(string="Success")    
    error_count = fields.Integer(string="Errors")      
    state = fields.Selection([
        ('success', 'Success'),
        ('partial', 'Partial'),                        
        ('failed', 'Failed'),
    ], string="Status")
    message = fields.Text(string="Message")             
    sftp_server_id = fields.Many2one(
        'choreograph.sage.sftp.server',                 
        string="SFTP Server",
    )