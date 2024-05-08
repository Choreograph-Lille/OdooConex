# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FtpLogging(models.Model):
    _name = "ftp.logging"
    _description = "SAGE ftp log"
    _rec_name = "file_name"

    file_name = fields.Char()
    export_date = fields.Date()
    file = fields.Binary()
    line_count = fields.Integer()

