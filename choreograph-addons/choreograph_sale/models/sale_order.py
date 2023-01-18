# -*- coding: utf-8 -*-

from odoo import api, fields, models

OPERATION_CONDITION_TYPE = {
    'file_processing': 'File Condition',
    'maj_condition': 'MAJ Condition',
    'sale_order': 'Sale Order Condition',
    'exclusion': 'Exclusion',
    'exclusion_so': 'Sale Order Exclusion',
    'comment': 'Comment',
}
OPERATION_TYPE = {
    'condition': 'Condition',
    'exclusion': 'Exclusion',
}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    show_operation_generation_button = fields.Boolean(default=True)
    operation_condition_ids = fields.One2many('operation.condition', 'order_id')
    new_condition_count = fields.Integer(compute='_compute_new_condition_count')
    catalogue_ids = fields.Many2many('res.partner.catalogue', 'sale_order_partner_catalogue_rel', 'sale_order_id', 'catalogue_id', 'Catalogues')
    prefulfill_study = fields.Boolean('Pre-fulfill study')
    related_base = fields.Many2one('retribution.base', string='Related base')
    data_conservation = fields.Char('Data conservation')
    receiver = fields.Char('Receiver')
    send_with = fields.Char('Send with')
    operation_type_id = fields.Many2one('project.project', 'Operation Type')
    total_retribution = fields.Float(compute="_compute_total_retribution")

    @api.depends('order_line')
    def _compute_total_retribution(self):
        for rec in self:
            rec.total_retribution = sum(rec.order_line.mapped('retribution_cost'))

    def action_generate_operation(self):
        self.order_line.sudo().with_company(self.company_id).with_context(is_operation_generation=True)._timesheet_service_generation()
        self.show_operation_generation_button = False

    def action_create_task_from_condition(self):
        for rec in self:
            for condition in self.operation_condition_ids.filtered(lambda c: not c.is_task_created and c.type != 'comment'):
                vals = {
                    'name': rec.name + '/' + OPERATION_TYPE[condition.operation_type] + '/' + OPERATION_CONDITION_TYPE[condition.type],
                    'partner_id': rec.partner_id.id,
                    'email_from': rec.partner_id.email,
                    'description': condition.note,
                    'sale_order_id': rec.id,
                    'user_ids': False,
                }
                vals['name'] += condition.subtype_id.name if condition.subtype_id else ''
                rec.project_ids.task_ids = [(0, 0, vals)]
                condition.is_task_created = True

    def _compute_new_condition_count(self):
        self.new_condition_count = len(self.operation_condition_ids.filtered(
            lambda c: not c.is_task_created and c.type != 'comment'))

    def _reset_show_operation_generation_button(self, vals):
        vals['show_operation_generation_button'] = True
        return vals

    @api.model
    def create(self, vals):
        vals = self._reset_show_operation_generation_button(vals)
        return super(SaleOrder, self).create(vals)
