# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class OperationGeneration(models.TransientModel):
    _name = 'operation.generation'
    _description = 'Operation Generation'

    order_id = fields.Many2one('sale.order')
    operation_selection = fields.Selection([('creation', 'Create a new operation'),
                                            ('association', 'Associate order with an existing operation')], default='creation')
    project_id = fields.Many2one('project.project', 'Operation')

    def action_validate(self):
        if self.operation_selection == 'creation':
            self.order_id.action_generate_operation()
        else:
            so_line_new_project = self.order_id.order_line.filtered(
                lambda sol: sol.is_service and sol.product_id.service_tracking in ['project_only', 'task_in_project'])
            if so_line_new_project:
                line = so_line_new_project[0]
                line.project_id = self.project_id.id
                line._timesheet_create_task(project=self.project_id)
                line._generate_milestone()
                self.project_id.write({
                    'sale_line_id': line.id,
                    'partner_id': self.order_id.partner_id.id
                })

                self.project_id.task_ids.write({
                    'sale_line_id': line.id,
                    'partner_id': self.order_id.partner_id.id,
                    'email_from': self.order_id.partner_id.email,
                })
                self.project_id.task_ids.filtered('parent_id').write({
                    'sale_line_id': self.id,
                    'sale_order_id': self.order_id.id,
                })
        self.order_id.show_operation_generation_button = False
