# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    customer_ids = fields.Many2many(domain=[('customer_rank', '>', 0)])
