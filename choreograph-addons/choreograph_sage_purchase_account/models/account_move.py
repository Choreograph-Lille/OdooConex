# -*- coding: utf-8 -*-

import paramiko
import logging

_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_file_name(self):
        prefix = self.env['ir.config_parameter'].sudo().get_param('choreograph_sage_purchase_account.prefix') or False
        suffix = self.env['ir.config_parameter'].sudo().get_param('choreograph_sage_purchase_account.suffix') or False

        file_name = f"{fields.Date.today().strftime('%Y%m%d')}.csv"
        if prefix:
            file_name = prefix + file_name
        if suffix:
            file_name += suffix
        return file_name

    def is_present_file(self, filename, listdir):
        if filename in listdir:
            return True
        else:
            return False


    def get_sftp_client(self, ftp_server):
        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Get path of key as attachment
        key_path = ftp_server.key_attachment_id._full_path(ftp_server.key_attachment_id.store_fname)
        passphrase = ftp_server.passphrase

        try:
            key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
            ssh_client.connect(ftp_server.host, ftp_server.port, ftp_server.username, pkey=key)
            with paramiko.SFTPClient.from_transport(ssh_client.get_transport()) as sftp:
                list_dir = sftp.listdir(f'/{ftp_server.output_path}')
                filename = self.get_file_name()
                if self.is_present_file(filename, list_dir):
                    _logger.info('File %s found' % filename)
                    return sftp
                else:
                    _logger.info('File not found')
                    return False
        except Exception as e:
            raise UserError(_('Could not etablish connexion to ftp server, reason %s') % e)



    @api.model
    def import_account_move_in_invoice(self):
        ftp_server = self.env['choreograph.sage.sftp.server'].search([('active', '=', True)], limit=1)
        if ftp_server:
            sftp = self.get_sftp_client(ftp_server)
        return True