# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _

OPERATION_CONDITION_TYPE = {
    'file_processing': 'File condition',
    'maj_condition': 'MAJ condition',
    'sale_order': 'Sale order condition',
    'exclusion': 'Exclusion',
    'exclusion_so': 'Sale order exclusion',
    'comment': 'Comment',
}
OPERATION_TYPE = {
     'condition': 'Condition',
     'exclusion': 'Exclusion',
}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    show_operation_generation_button = fields.Boolean(default=True)
    operation_condition_ids = fields.One2many('operation.condition', 'order_id')
    new_condition_count = fields.Integer(compute='_compute_new_condition_count')
    # studio custom
    catalogue_ids = fields.Many2many('res.partner.catalogue', string='Catalogue')
    prefulfill_study = fields.Boolean('Pre-fulfill study')
    related_base = fields.Char('Related base')
    data_conservation = fields.Char('Data conservation')
    receiver = fields.Char('Receiver')
    send_with = fields.Char('Send with')
    operation_type_id = fields.Many2one('project.project', string='Operation type')

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
        self.new_condition_count = len(self.operation_condition_ids.filtered(lambda c: not c.is_task_created and c.type != 'comment'))


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_service_generation(self):
        if self._context.get('is_operation_generation'):
            super()._timesheet_service_generation()
