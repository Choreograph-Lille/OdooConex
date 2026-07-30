# -*- coding: utf-8 -*-

import paramiko
from odoo import _, fields, models


class ChoreographSageSftpServer(models.Model):
    _name = "choreograph.sage.sftp.server"
    _description = "SAGE SFTP server configuration (Sage to Odoo)"

    name = fields.Char(string="Server Name", required=True)
    host = fields.Char(required=True)
    port = fields.Char(required=True, default='22')
    username = fields.Char(required=True)
    passphrase = fields.Char(required=True)
    key_attachment_id = fields.Many2one("ir.attachment", required=True)

    output_path = fields.Char(
        string="Output Directory",
        required=True,
        help="Output directory for the SFTP server (e.g., /Output)",
    )

    active = fields.Boolean(default=True)
    connection_status = fields.Char()

    def _get_sftp_client(self):
        """
        Builds and returns (ssh_client, sftp_client).
        Same authentication logic as ChoreographSageFtpServer,
        but via SSH/SFTP instead of FTP.
        """
        self.ensure_one()

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        key_path = self.key_attachment_id._full_path(self.key_attachment_id.store_fname)
        key = paramiko.RSAKey.from_private_key_file(key_path, password=self.passphrase)

        ssh_client.connect(self.host, int(self.port), self.username, pkey=key)
        sftp_client = ssh_client.open_sftp()
        return ssh_client, sftp_client

    def action_connection_test(self):
        ssh_client = None
        sftp_client = None
        try:
            ssh_client, sftp_client = self._get_sftp_client()

            try:
                sftp_client.stat(self.output_path)
            except FileNotFoundError:
                self.connection_status = _(
                    "Connection successful, but the directory '%s' is not found.",
                    self.output_path,
                )
                return

            self.connection_status = _("Connection success")

        except Exception as e:
            self.connection_status = _("Connection failed: %s", str(e))

        finally:
            if sftp_client:
                sftp_client.close()
            if ssh_client:
                ssh_client.close()