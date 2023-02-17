# -*- coding: utf-8 -*-

from datetime import date
from dateutil import tz
from pytz import timezone, utc, UTC

from odoo import _, api, fields, models
from odoo.exceptions import UserError
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
    operation_type_id = fields.Many2one('project.project', compute='_compute_operation_type_id', store=True)
    can_display_redelivery = fields.Boolean(compute='_compute_can_display_redelivery')

    @api.depends('project_ids')
    def _compute_operation_type_id(self):
        for rec in self:
            rec.operation_type_id = rec.project_ids[0] if rec.project_ids else False

    @api.depends('operation_type_id.stage_id')
    def _compute_can_display_redelivery(self):
        STAGE_PROJECT = [
            self.env.ref('choreograph_project.planning_project_stage_in_progress').id,
            self.env.ref('choreograph_project.planning_project_stage_delivery').id,
            self.env.ref('choreograph_project.planning_project_stage_terminated').id
        ]
        for rec in self:
            rec.can_display_redelivery = rec.operation_type_id.stage_id.id in STAGE_PROJECT if rec.operation_type_id else False

    # def write(self, vals):
    #     res = super(SaleOrder, self).write(vals)
    #     self._check_operation_values(vals)
    #     return res

    @api.onchange('potential_return')
    def onchange_potential_return(self):
        self.study_delivery = self.potential_return
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

    def action_redelivery(self):
        if len(self.project_ids) > 1:
            raise UserError(_("the SO contains several projects"))
        project_id = self.project_ids[0]
        redelivery_type = self.env.context.get('redelivery_type')
        if redelivery_type == 'studies':
            project_id.js_redelivery_studies()
        else:
            project_id.js_redelivery_prod()

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if vals.get('commitment_date'):
            self._update_date_deadline()
        return res

    def _update_date_deadline(self):
        for rec in self:
            tz = timezone(self.env.user.tz or self.env.context.get('tz') or 'UTC')
            date = utc.localize(rec.commitment_date).astimezone(tz)
            rec.tasks_ids.filtered(lambda t: t.task_number in ['80', '65', '40', '85', '90', '45', '50', '25', '30', '35']).write({
                'date_deadline': date,
            })
