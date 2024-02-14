# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class OperationSegment(models.Model):
    _name = 'operation.segment'
    _inherit = ['field.tracking.message.mixin']
    _description = 'Segment'

    order_id = fields.Many2one('sale.order', 'Sale Order')
    segment_number = fields.Integer(compute='_compute_segment_number', tracking=True)
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

    @api.model
    def _track_message_title_unlink(self):
        return _("Segment deleted")

    def _field_to_track(self):
        self.ensure_one()
        return ["segment_number", "model_selection", "ranking", "quantity", "depth", "keycode", "civility", "comment"]

    def _get_body_message_track(self):
        return _('Segment line : %s') % self.sequence

    def _compute_segment_number(self):
        for rec in self:
            rec.segment_number = rec.sequence
