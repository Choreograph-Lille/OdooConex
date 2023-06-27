# -*- coding: utf-8 -*-

from odoo import fields, models, api


class OperationSegment(models.Model):
    _name = 'operation.segment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    order_id = fields.Many2one('sale.order', 'Sale Order')
    segment_number = fields.Integer(tracking=True)
    model_selection = fields.Char('Model/Selection', tracking=True)
    name = fields.Char('Segment Name', tracking=True)
    quantity = fields.Integer(tracking=True)
    depth = fields.Integer(tracking=True)
    keycode = fields.Char(tracking=True)
    ranking = fields.Selection([('ranked', 'Ranked'), ('random', 'Random')], tracking=True)
    civility = fields.Selection([
        ('male', 'Males'),
        ('female', 'Females'),
        ('other', 'Others')
    ], tracking=True)
    comment = fields.Char(tracking=True)
    task_id = fields.Many2one('project.task', 'Task')
    sequence = fields.Integer(default=1)
