# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    role_id = fields.Many2one('choreograph.role', string='Role')
    # fields from SO
    sms_coupling = fields.Boolean(related='sale_order_id.sms_coupling')
    show_sms_coupling = fields.Boolean(compute='_compute_operation_fields')

    phone_coupling = fields.Boolean(related='sale_order_id.phone_coupling')
    show_phone_coupling = fields.Boolean(compute='_compute_operation_fields')

    email_coupling = fields.Boolean(related='sale_order_id.email_coupling')
    show_email_coupling = fields.Boolean(compute='_compute_operation_fields')

    @api.onchange('role_id')
    def onchange_role_id(self):
        partner_role = self.project_id.partner_id.role_ids.filtered(lambda r: r.role_id.id == self.role_id.id)
        self.user_ids = [(6, 0, self.role_id and self.project_id.partner_id and partner_role and partner_role[0].user_ids.ids or [])]

    def _compute_operation_fields(self):
        self.show_sms_coupling = self.task_type == self.sale_order_id.sms_coupling_task_type_id
        self.show_phone_coupling = self.task_type == self.sale_order_id.phone_coupling_task_type_id
        self.show_email_coupling = self.task_type == self.sale_order_id.email_coupling_task_type_id
