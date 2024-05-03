# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ChoreographSageFtpServer(models.Model):
    _name = "choreograph.sage.ftp.server"
    _description = "SAGE ftp server configuration"
    _rec_name = 'host'

    host = fields.Char()
    port = fields.Char()
    path = fields.Char()
    active = fields.Boolean()
