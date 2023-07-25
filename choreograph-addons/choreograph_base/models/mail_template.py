# -*- coding: utf-8 -*-
from odoo import models, fields


class MailTemplate(models.Model):
    _inherit = 'mail.template'

    user_url = fields.Selection([('gao', 'GAO'), ('mymodel', 'MyModel')])
