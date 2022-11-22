# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_type = fields.Many2one('choreograph.project.task.type', string='Task type')

    def _compute_operation_fields(self):
        self.show_sms_coupling = self.task_type == self.sale_order_id.sms_coupling_task_type_id
