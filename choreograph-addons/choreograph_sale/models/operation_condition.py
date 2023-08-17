# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import html_escape
from odoo.tools.misc import format_date

TASK_NUMBER = [(str(n), str(n)) for n in range(5, 100, 5)]
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


class OperationCondition(models.Model):
    _name = 'operation.condition'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
                                 'condition_id', 'sale_order_id', 'Sale Order')
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
                                                  + rec.subtype] if rec.subtype in ['client_file', 'update', 'update_repoussoir'] else False

    def write(self, vals):
        res = super(OperationCondition, self).write(vals)
        self._update_task_values()
        return res

    def _update_task_values(self):
        for rec in self:
            if rec.task_id:
                rec.task_id.write({
                    'note': rec.note,
                    'date_deadline': rec.operation_date,
                    'campaign_file_name': rec.file_name,
                    'task_number': rec.task_number,
                })

    def unlink(self):
        self.task_id.unlink()
        self._log_unlinked_operation_condition()
        return super(OperationCondition, self).unlink()

    def _log_unlinked_operation_condition(self):
        for rec in self:
            body_msg = _("Condition/Exclusion deleted")
            tracking_msg = ""
            for f in self._field_to_track_on_unlink():
                tracking_msg += rec._format_tracked_field_on_unlink(f)
            if tracking_msg:
                body_msg += f"<ul> {tracking_msg} </ul>"
            rec._message_log(body=body_msg)

    @api.model
    def _field_to_track_on_unlink(self):
        return ["operation_type", "subtype", "operation_date", "file_name", "note", "order_ids"]

    def _format_tracked_field_on_unlink(self, field_name):
        self.ensure_one()
        field_obj = self._fields[field_name]
        if getattr(self, field_name):
            if field_obj.type == "date":
                field_value = format_date(self.env, getattr(self, field_name), date_format="dd/MM/yyyy")
            elif field_obj.type == "selection":
                field_desc = field_obj.get_description(self.env)
                field_info = dict(field_desc.get('selection'))
                field_value = field_info.get(getattr(self, field_name))
            elif field_obj.type == "many2many":
                field_value = ", ".join(getattr(self, field_name).mapped("display_name"))
            else:
                field_value = getattr(self, field_name)
            return f"<li>{field_value} <i>({html_escape(field_obj._description_string(self.env))})</i></li>"
        return ""

class OperationConditionType(models.Model):
    _name = 'operation.condition.subtype'

    name = fields.Char()
