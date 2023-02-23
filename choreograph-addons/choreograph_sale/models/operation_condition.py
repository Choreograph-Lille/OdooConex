from odoo import api, fields, models

TASK_NUMBER = [(str(n), str(n)) for n in range(5, 100, 5)]
SUBTYPE = [('client_file', 'Client File'), ('sale_order', 'Sale Order'), ('comment', 'Comment'), ('update', 'Update'), ('update_repoussoir', 'Update Repoussoir')]
CONDITION_SUBTYPE = [('client_file', 'Client File'), ('update', 'Update'), ('sale_order', 'Sale Order'), ('comment', 'Comment')]
EXCLUSION_SUBTYPE = [('client_file', 'Client File'), ('update_repoussoir', 'Update Repoussoir'), ('sale_order', 'Sale Order'), ('comment', 'Comment')]
SUBTYPE_TASK_NUMBER = {
    'condition_client_file': '15',
    'condition_update': '5',
    'exclusion_client_file': '15',
    'exclusion_update_repoussoir': '10',
}


class OperationCondition(models.Model):
    _name = 'operation.condition'
    _description = 'Operation Condition'

    operation_date = fields.Date('Operation date')
    note = fields.Text('Information')
    order_id = fields.Many2one('sale.order')
    is_task_created = fields.Boolean('Is Task Created?')
    operation_type = fields.Selection([
        ('condition', 'Condition'),
        ('exclusion', 'Exclusion')],
        default='condition',
        required=True)
    file_name = fields.Char()
    task_number = fields.Selection(TASK_NUMBER, compute='_compute_task_number')
    subtype = fields.Selection(SUBTYPE, required=True, compute='_compute_subtype')
    condition_subtype = fields.Selection(CONDITION_SUBTYPE, required=True, default='client_file')
    exclusion_subtype = fields.Selection(EXCLUSION_SUBTYPE, required=True, default='client_file')
    order_ids = fields.Many2many('sale.order', 'operation_condition_sale_order_rel', 'condition_id', 'sale_order_id', 'Sale Order')
    task_id = fields.Many2one('project.task')

    @api.depends('operation_type', 'condition_subtype', 'exclusion_subtype')
    def _compute_subtype(self):
        for rec in self:
            rec.subtype = rec.condition_subtype if rec.operation_type == 'condition' else rec.exclusion_subtype

    @api.depends('subtype')
    def _compute_task_number(self):
        for rec in self:
            rec.task_number = SUBTYPE_TASK_NUMBER[rec.operation_type + '_' + rec.subtype] if rec.subtype in ['client_file', 'update', 'update_repoussoir'] else False
