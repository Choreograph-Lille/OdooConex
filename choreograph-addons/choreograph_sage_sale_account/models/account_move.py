import paramiko
import logging

_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_file_name(self):
        prefix = self.env['ir.config_parameter'].sudo().get_param(
            'choreograph_sage_sale_account.prefix') or ''
        suffix = self.env['ir.config_parameter'].sudo().get_param(
            'choreograph_sage_sale_account.suffix') or ''
        date_str = fields.Date.today().strftime('%Y%m%d')
        return f"{prefix}{date_str}{suffix}"

    def is_present_file(self, filename, listdir):
        return filename in listdir

    def get_sftp_client(self, ftp_server):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        key_path = ftp_server.key_attachment_id._full_path(
            ftp_server.key_attachment_id.store_fname)

        try:
            key = paramiko.RSAKey.from_private_key_file(
                key_path, password=ftp_server.passphrase)
            ssh_client.connect(
                ftp_server.host, ftp_server.port,
                ftp_server.username, pkey=key)

            sftp = ssh_client.open_sftp()
            list_dir = sftp.listdir(ftp_server.output_path)
            filename = self.get_file_name()

            if self.is_present_file(filename, list_dir):
                _logger.info('Sage sale file found: %s', filename)
                return ssh_client, sftp, filename
            else:
                _logger.info('Sage sale file not found: %s', filename)
                sftp.close()
                ssh_client.close()
                return None, None, filename

        except Exception as e:
            ssh_client.close()
            raise UserError(
                _('Could not establish connection to SFTP server: %s') % e)

    @api.model
    def import_account_move_out_invoice(self):
        ftp_server = self.env['choreograph.sage.sftp.server'].search(
            [('active', '=', True)], limit=1)

        if not ftp_server:
            _logger.warning('Sage sale import: no active SFTP server found.')
            return False

        ssh_client, sftp, filename = self.get_sftp_client(ftp_server)

        if not sftp:
            _logger.warning('Sage sale import: file %s not found on SFTP.', filename)
            return False

        try:
            pass
        finally:
            sftp.close()
            ssh_client.close()

        return True