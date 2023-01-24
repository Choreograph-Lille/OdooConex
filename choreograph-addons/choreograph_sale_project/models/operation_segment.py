# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class OperationSegment(models.Model):
    _name = "operation.segment"

    order_id = fields.Many2one('sale.order', 'Sale Order')
    segment_number = fields.Integer('Segment Number')
    model_selection = fields.Char('Model/Selection')
    name = fields.Char('Name')
    quantity = fields.Integer('Quantity')
    depth = fields.Char('Depth')
    keycode = fields.Char('Keycode')
    ranking = fields.Char('Ranking')
    civility = fields.Char('Civility')
    comment = fields.Char('Comment')
