# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class OperationConditionSubtype(models.Model):
    _name = 'operation.condition.subtype'
    _description = 'Operation Condition Subtype'

    name = fields.Char('Subtype name')
    type = fields.Selection([
        ('file_processing', 'File condition'),
        ('maj_condition', 'MAJ condition'),
        ('sale_order', 'Sale order condition'),
        ('exclusion', 'Exclusion'),
        ('exclusion_so', 'Sale order exclusion')
    ], required=True, string='Type name')
    default_fill = fields.Boolean('Default fill')


class OperationCondition(models.Model):
    _name = 'operation.condition'
    _description = 'Operation Condition'

    operation_type = fields.Selection([('condition', 'Condition'), ('exclusion', 'Exclusion')], string='Operation type',
                                      required=True)
    type = fields.Selection([
        ('file_processing', 'File condition'),
        ('maj_condition', 'MAJ condition'),
        ('sale_order', 'Sale order condition'),
        ('exclusion', 'Exclusion'),
        ('exclusion_so', 'Sale order exclusion'),
        ('comment', 'Comment')
    ], required=True, string='Type')

    subtype_id = fields.Many2one('operation.condition.subtype')
    operation_date = fields.Date('Operation date')
    note = fields.Text('Information')
    order_id = fields.Many2one('sale.order')
    is_task_created = fields.Boolean()

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

