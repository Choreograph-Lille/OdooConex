from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sftp_import_server_id = fields.Many2one('choreograph.sage.sftp.server', string="SFTP Server", config_parameter='choreograph_sage_sftp_import.sftp_server_id')

    