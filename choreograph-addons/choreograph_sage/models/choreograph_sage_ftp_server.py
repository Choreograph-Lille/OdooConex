# -*- coding: utf-8 -*-

import paramiko
from odoo import models, fields, api, _



class ChoreographSageFtpServer(models.Model):
    _name = "choreograph.sage.ftp.server"
    _description = "SAGE ftp server configuration"
    _rec_name = 'host'

    host = fields.Char(required=True)
    port = fields.Char(required=True)
    path = fields.Char(required=True)
    passphrase = fields.Char(required=True)
    username = fields.Char(required=True)
    key_attachment_id = fields.Many2one("ir.attachment", required=True)
    active = fields.Boolean()
    connection_status = fields.Char()

    def action_connection_test(self):
        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Get path of key as attachment
        key_path = self.key_attachment_id._full_path(self.key_attachment_id.store_fname)
        passphrase = self.passphrase
        try:
            key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
            # Connect to server
            ssh_client.connect(self.host, self.port, self.username, pkey=key)
            self.connection_status = _("Connection success")
        except Exception as e:
            self.connection_status = _("Connection failed: %s",str(e))
        finally:
            ssh_client.close()
