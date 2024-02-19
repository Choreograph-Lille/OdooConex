# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import html_escape
from odoo.tools.misc import format_date

TASK_NUMBER = [(str(n), str(n)) for n in range(5, 100, 5)]
OPERATION_TYPE = {
    'condition': 'Condition',
    'exclusion': 'Exclusion',
}
SUBTYPE = [('client_file', _('Client File')), ('sale_order', _('Sale Order')), ('comment', _('Comment')),
           ('update', _('Update')), ('update_repoussoir', _('Update Repoussoir'))]
CONDITION_SUBTYPE = [('client_file', 'Client File'), ('update', 'Update'),
                     ('sale_order', 'Sale Order'), ('comment', 'Comment')]
EXCLUSION_SUBTYPE = [('client_file', 'Client File'), ('update_repoussoir', 'Update Repoussoir'),
                     ('sale_order', 'Sale Order'), ('comment', 'Comment')]
SUBTYPE_TASK_NUMBER = {
    'condition_client_file': '15',
    'condition_update': '5',
    'exclusion_client_file': '15',
    'exclusion_update_repoussoir': '10',
}
SUBTYPES = dict(SUBTYPE)


class OperationCondition(models.Model):
    _name = 'operation.condition'
    _inherit = ['field.tracking.message.mixin']
    _description = 'Operation Condition'

    operation_date = fields.Date('Operation date', tracking=True)
    note = fields.Text('Information', tracking=True)
    order_id = fields.Many2one('sale.order')
    is_task_created = fields.Boolean('Is Task Created?')
    operation_type = fields.Selection([
        ('condition', 'Condition'),
        ('exclusion', 'Exclusion')],
        default='condition',
        required=True, tracking=True)
    file_name = fields.Char(tracking=True)
    task_number = fields.Selection(TASK_NUMBER, compute='_compute_task_number')
    subtype = fields.Selection(SUBTYPE, required=True, compute='_compute_subtype', tracking=True)
    condition_subtype = fields.Selection(CONDITION_SUBTYPE, required=True, default='client_file', tracking=True)
    exclusion_subtype = fields.Selection(EXCLUSION_SUBTYPE, required=True, default='client_file')
    order_ids = fields.Many2many('sale.order', 'operation_condition_sale_order_rel',
                                 'condition_id', 'sale_order_id', 'Sale Order', tracking=True)
    task_id = fields.Many2one('project.task')
    partner_id = fields.Many2one('res.partner')
    sequence = fields.Integer(default=1)

    @api.depends('operation_type', 'condition_subtype', 'exclusion_subtype')
    def _compute_subtype(self):
        for rec in self:
            rec.subtype = rec.condition_subtype if rec.operation_type == 'condition' else rec.exclusion_subtype

    @api.depends('subtype')
    def _compute_task_number(self):
        for rec in self:
            rec.task_number = SUBTYPE_TASK_NUMBER[rec.operation_type + '_'
                                                  + rec.subtype] if rec.subtype in ['client_file', 'update',
                                                                                    'update_repoussoir'] else False

    def write(self, vals):
        res = super(OperationCondition, self).write(vals)
        if any(task in vals for task in ['operation_type', 'condition_subtype', 'exclusion_subtype']):
            self.check_subtype()
        self._update_task_values()
        return res

    def check_subtype(self):
        for rec in self:
            subtype_blacklist = ['sale_order', 'comment']
            if rec.subtype in subtype_blacklist:
                rec.task_id.unlink()
                rec.is_task_created = False

    def get_task_name(self):
        return OPERATION_TYPE[self.operation_type] + '/' + _(SUBTYPES[self.subtype])

    def _update_task_values(self):
        for rec in self:
            if rec.task_id:
                rec.task_id.write({
                    'name': rec.get_task_name(),
                    'note': rec.note,
                    'date_deadline': rec.order_id.get_next_non_day_off(rec.operation_date),
                    'campaign_file_name': rec.file_name,
                    'task_number': rec.task_number,
                })

    def unlink(self):
        self.task_id.unlink()
        return super(OperationCondition, self).unlink()

    @api.model
    def _track_message_title_unlink(self):
        return _("Condition/Exclusion deleted")

    def _field_to_track(self):
        self.ensure_one()
        field_to_track = ["operation_type", "subtype", "operation_date", "note"]
        if (self.operation_type == "condition" and self.condition_subtype == "client_file") or (
                self.operation_type == "exclusion" and self.exclusion_subtype == "client_file"):
            field_to_track += ["file_name"]
        elif (self.operation_type == "condition" and self.condition_subtype == "sale_order") or (
                self.operation_type == "exclusion" and self.exclusion_subtype == "sale_order"):
            field_to_track += ["order_ids"]
        return field_to_track

    def _get_body_message_track(self):
        return _('Condition/Exclusion line : %s') % self.sequence


class OperationConditionType(models.Model):
    _name = 'operation.condition.subtype'
    _description = 'Operation Condition Subtype'

    name = fields.Char()
