# -*- coding: utf-8 -*-

from datetime import date

from odoo import api, fields, models

from odoo.addons.choreograph_sale.models.sale_order import REQUIRED_TASK_NUMBER

PROVIDER_DELIVERY_NUMBER = '75'


class SaleOrder(models.Model):
    _inherit = "sale.order"

    potential_return = fields.Boolean()
    study_delivery = fields.Boolean()
    presentation = fields.Boolean()
    potential_return_task_id = fields.Many2one(
        'project.task', 'Potential Return Task')
    study_delivery_task_id = fields.Many2one('project.task', 'Study Delivery Task')
    presentation_task_id = fields.Many2one('project.task', 'Presentation Task')

    show_provider_delivery = fields.Boolean(compute='_compute_show_provider_delivery')
    operation_provider_delivery_ids = fields.One2many(
        'operation.provider.delivery', 'order_id', 'Provider Delivery Tasks')
    comment = fields.Text()
    quantity_to_deliver = fields.Integer()
    to_validate = fields.Boolean()
    segment_ids = fields.One2many('operation.segment', 'order_id', 'Segment')
    repatriate_information = fields.Boolean('Repatriate Informations On Delivery Informations Tab')

    # def write(self, vals):
    #     res = super(SaleOrder, self).write(vals)
    #     self._check_operation_values(vals)
    #     return res

    @api.onchange('potential_return')
    def onchange_potential_return(self):
        if self.potential_return:
            self._unarchive_task('potential_return')
        else:
            self._archive_task('potential_return')

    @api.onchange('study_delivery')
    def onchange_study_delivery(self):
        if self.study_delivery:
            self._unarchive_task('study_delivery')
        else:
            self._archive_task('study_delivery')

    @api.onchange('presentation')
    def onchange_presentation(self):
        if self.presentation:
            self._unarchive_task('presentation')
        else:
            self._archive_task('presentation')

    def _get_operation_task(self, operation_task, active):
        for rec in self:
            return self.env['project.task'].search(
                    ['&', ('display_project_id', '!=', 'False'), '|', ('sale_line_id', 'in', rec.order_line.ids),
                     ('sale_order_id', '=', rec.id), ('active', '=', active),
                     ('task_number', '=', REQUIRED_TASK_NUMBER[operation_task])])

    def _unarchive_task(self, operation_task):
        for rec in self:
            task = rec._get_operation_task(operation_task, False) or rec._get_operation_task(operation_task, True)
            task.write({
                'active': True,
            })
            rec.write({
                operation_task + '_task_id': task.id
            })

    def _archive_task(self, operation_task):
        for rec in self:
            task = rec._get_operation_task(operation_task, True)
            task.write({
                'active': False,
            })

    @api.depends('order_line')
    def get_provider_delivery_template(self):
        line_with_project = self.get_operation_product()
        if line_with_project:
            provider_template = line_with_project[0].operation_template_id.task_ids.filtered(
                lambda t: t.task_number == PROVIDER_DELIVERY_NUMBER)
            return provider_template if provider_template else False
        return False

    def _compute_show_provider_delivery(self):
        self.show_provider_delivery = True if self.get_provider_delivery_template() else False

    @api.depends('potential_return', 'study_delivery', 'presentation')
    def _compute_operation_task(self):
        for rec in self:
            rec.potential_return_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == REQUIRED_TASK_NUMBER['potential_return']).id or False
            rec.study_delivery_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == REQUIRED_TASK_NUMBER['study_delivery']).id or False
            rec.presentation_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == REQUIRED_TASK_NUMBER['presentation']).id or False

    def action_generate_operation(self):
        super(SaleOrder, self).action_generate_operation()
        provider_delivery_template = self.get_provider_delivery_template()
        if provider_delivery_template:
            self.with_context(no_create_delivery_task=True).write({
                'operation_provider_delivery_ids': [(0, 0, {
                    'delivery_date': provider_delivery_template.date_deadline or date.today(),
                    'task_id': self.tasks_ids.filtered(lambda t: t.task_number == PROVIDER_DELIVERY_NUMBER).id
                })]
            })
