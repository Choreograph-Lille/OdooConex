# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_type_id = fields.Many2one('choreograph.project.task.type', string='Task type')
    # fields from SO
    sms_coupling = fields.Boolean(related='sale_order_id.sms_coupling')
    show_sms_coupling = fields.Boolean(compute='_compute_operation_fields')

    phone_coupling = fields.Boolean(related='sale_order_id.phone_coupling')
    show_phone_coupling = fields.Boolean(compute='_compute_operation_fields')

    email_coupling = fields.Boolean(related='sale_order_id.email_coupling')
    show_email_coupling = fields.Boolean(compute='_compute_operation_fields')

    def _compute_operation_fields(self):
        for rec in self:
            rec.show_sms_coupling = rec.task_type_id == rec.sale_order_id.sms_coupling_task_type_id
            rec.show_phone_coupling = rec.task_type_id == rec.sale_order_id.phone_coupling_task_type_id
            rec.show_email_coupling = rec.task_type_id == rec.sale_order_id.email_coupling_task_type_id
