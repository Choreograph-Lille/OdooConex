# -*- coding: utf-8 -*-

from odoo import fields, models


class TrapAddress(models.Model):
    _name = 'trap.address'

    name = fields.Char('Trap Addresses')
    task_id = fields.Many2one('project.task')
    segment_number = fields.Char()
    bc_number = fields.Char('BC Number')
