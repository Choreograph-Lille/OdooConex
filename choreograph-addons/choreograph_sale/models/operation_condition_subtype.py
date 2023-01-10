# -*- coding: utf-8 -*-

from odoo import fields, models, api


class OperationConditionSubtype(models.Model):
    _name = 'operation.condition.subtype'
    _description = 'Operation Condition Subtype'

    name = fields.Char('Subtype name')
    type = fields.Selection([
        ('file_processing', 'File Condition'),
        ('maj_condition', 'MAJ Condition'),
        ('sale_order', 'Sale Order Condition'),
        ('exclusion', 'Exclusion'),
        ('exclusion_so', 'Sale Order Exclusion')
    ], 'Type Name', required=True)
    default_fill = fields.Boolean('Default Fill')

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('filter_by_parent_type'):
            args += [('type', '=', self._context.get('filter_by_parent_type'))]
        return super(OperationConditionSubtype, self)._search(args, offset=offset, limit=limit, order=order, count=count,
                                                              access_rights_uid=access_rights_uid)
