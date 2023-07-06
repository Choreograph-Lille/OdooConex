# -*- coding: utf-8 -*-

from odoo import fields, models


class OperationProviderDelivery(models.Model):
    _name = 'operation.provider.delivery'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    order_id = fields.Many2one('sale.order', 'Sale Order')
    delivery_date = fields.Date('Date', tracking=True)
    task_id = fields.Many2one('project.task', 'Task', tracking=True)
    sequence = fields.Integer(default=1)

    def write(self, vals):
        res = super(OperationProviderDelivery, self).write(vals)
        for rec in self:
            if 'delivery_date' in vals:
                rec.update_task_date_deadline()
        return res

    def update_task_date_deadline(self):
        self.task_id.date_deadline = self.delivery_date
