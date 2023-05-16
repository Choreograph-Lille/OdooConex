# -*- coding: utf-8 -*-


from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    disable_followers = fields.Boolean('Disable customer subscription on a model')
