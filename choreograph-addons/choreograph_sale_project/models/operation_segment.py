# -*- coding: utf-8 -*-

from odoo import fields, models


class OperationSegment(models.Model):
    _name = "operation.segment"

    order_id = fields.Many2one('sale.order', 'Sale Order')
    segment_number = fields.Integer()
    model_selection = fields.Char('Model/Selection')
    name = fields.Char()
    quantity = fields.Integer()
    depth = fields.Char()
    keycode = fields.Char()
    ranking = fields.Char()
    civility = fields.Char()
    comment = fields.Char()
