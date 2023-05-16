# -*- coding: utf-8 -*-

from odoo import fields, models, api


class OperationSegment(models.Model):
    _name = "operation.segment"

    order_id = fields.Many2one('sale.order', 'Sale Order')
    segment_number = fields.Integer()
    model_selection = fields.Char('Model/Selection')
    name = fields.Char("Segment Name")
    quantity = fields.Integer()
    depth = fields.Integer()
    keycode = fields.Char()
    ranking = fields.Selection([('ranked', 'Ranked'), ('random', 'Random')])
    civility = fields.Selection([
        ('male', 'Males'),
        ('female', 'Females'),
        ('other', 'Others')
    ])
    comment = fields.Char()
