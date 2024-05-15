# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class FtpLogging(models.Model):
    _name = "ftp.logging"
    _description = "SAGE ftp log"
    _rec_name = "file_name"

    file_name = fields.Char()
    export_date = fields.Date()
    attachment_id = fields.Many2one('ir.attachment')
    file = fields.Binary()
    type = fields.Selection([
        ('customer','Customer'),
        ('supplier','Supplier')
    ])
    line_count = fields.Integer()
    state = fields.Selection([
        ('failed', 'Failed'),
        ('success','Success')
    ])
    message= fields.Char()

