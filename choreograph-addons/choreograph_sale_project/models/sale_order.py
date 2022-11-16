# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # operation fields
    sms_coupling = fields.Boolean()
    sms_coupling_task_type_id = fields.Many2one('choreograph.project.task.type', string='Task type')
