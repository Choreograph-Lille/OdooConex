# -*- coding: utf-8 -*-

from odoo import api, fields, models


class OperationProviderDelivery(models.Model):
    _name = "operation.provider.delivery"

    order_id = fields.Many2one('sale.order', 'Sale Order')
    delivery_date = fields.Date('Date', required=1, compute='compute_delivery_date', inverse='inverse_delivery_date')
    task_id = fields.Many2one('project.task', 'Task')

    @api.model
    def create(self, vals):
        res = super(OperationProviderDelivery, self).create(vals)
        res.create_delivery_task()
        return res

    @api.depends('task_id.date_deadline')
    def compute_delivery_date(self):
        for rec in self:
            rec.delivery_date = rec.task_id.date_deadline

    def inverse_delivery_date(self):
        for rec in self:
            rec.task_id.date_deadline = rec.delivery_date

    def create_delivery_task(self):
        for rec in self:
            if not self._context.get('no_create_delivery_task'):
                task_template = rec.order_id.get_provider_delivery_template()
                if task_template:
                    rec.task_id = task_template[0].copy()
                    rec.task_id.write({
                        'name': '%s (%s)' % (task_template[0].name, str(len(task_template))),
                        'date_deadline': rec.delivery_date,
                        'project_id': rec.order_id.get_operation_product().project_id.id
                    })
