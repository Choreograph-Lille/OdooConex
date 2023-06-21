# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

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
        return super(OperationCondition, self).unlink()


class OperationConditionType(models.Model):
    _name = 'operation.condition.subtype'

    name = fields.Char()
