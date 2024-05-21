# -*- coding: utf-8 -*-

from odoo import models, fields, api


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
