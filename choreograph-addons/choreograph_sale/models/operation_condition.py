from odoo import api, fields, models

TASK_NUMBER = [(str(n), str(n)) for n in range(5, 100, 5)]


class OperationCondition(models.Model):
    _name = 'operation.condition'
    _description = 'Operation Condition'

    subtype_id = fields.Many2one('operation.condition.subtype')
    operation_date = fields.Date('Operation date')
    note = fields.Text('Information')
    order_id = fields.Many2one('sale.order')
    is_task_created = fields.Boolean('Is Task Created?')
    operation_type = fields.Selection([
        ('condition', 'Condition'),
        ('exclusion', 'Exclusion')],
        required=True)
    type = fields.Selection([
        ('file_processing', 'File Condition'),
        ('maj_condition', 'MAJ Condition'),
        ('sale_order', 'Sale Order Condition'),
        ('exclusion', 'Exclusion'),
        ('exclusion_so', 'Sale Order Exclusion'),
        ('comment', 'Comment')
    ], required=True)
    file_name = fields.Char()
    task_number = fields.Selection(TASK_NUMBER)

    @api.onchange('type')
    def _onchange_type(self):
        subtypes = self.env['operation.condition.subtype'].search([('type', '=', self.type)])
        if subtypes and subtypes.filtered(lambda s: s.default_fill):
            self.subtype_id = subtypes.filtered(lambda s: s.default_fill)[0]
        else:
            self.subtype_id = False
        domain = {'domain': {
            'subtype_id': [('id', 'in', subtypes.ids)]
        }}
        return domain
