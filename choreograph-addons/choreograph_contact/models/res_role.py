# -*- coding: utf-8 -*-

from odoo import models, fields


class ChoreographRole(models.Model):
    _name = 'res.role'
    _description = 'Res Role'

    name = fields.Char()
