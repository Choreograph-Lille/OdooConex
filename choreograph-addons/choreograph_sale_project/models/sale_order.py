# -*- coding: utf-8 -*-

from datetime import date
from pytz import timezone, utc

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.addons.choreograph_sale.models.sale_order import REQUIRED_TASK_NUMBER
from odoo.addons.choreograph_project.models.project_project import TODO_TASK_STAGE

PROVIDER_DELIVERY_NUMBER = '75'
SMS_TASK_NUMBER = '50'
EMAIL_TASK_NUMBER = '45'
CHECK_TASK_STAGE_NUMBER = '10'
OPERATION_TASK_NUMBER = {
    'potential_return': '25',
    'study_delivery': '30',
    'presentation': '35',
    'study_global': '20'
}
CAMPAIGN_TASK_NAME = {
    '45': _('Email Campaign'),
    '50': _('SMS Campaign'),
}


class SaleOrder(models.Model):
    _inherit = "sale.order"

    potential_return = fields.Boolean(copy=False)
    study_delivery = fields.Boolean(copy=False)
    presentation = fields.Boolean(copy=False)
    potential_return_task_id = fields.Many2one(
        'project.task', 'Potential Return Task', copy=False)
    study_delivery_task_id = fields.Many2one('project.task', 'Study Delivery Task', copy=False)
    presentation_task_id = fields.Many2one('project.task', 'Presentation Task', copy=False)
    study_global_task_id = fields.Many2one('project.task', 'Study Global Task', copy=False)
    potential_return_date = fields.Date(copy=False)
    study_delivery_date = fields.Date(copy=False)
    presentation_date = fields.Date(copy=False)

    operation_provider_delivery_ids = fields.One2many(
        'operation.provider.delivery', 'order_id', 'Provider Delivery Tasks')
    comment = fields.Text()
    quantity_to_deliver = fields.Integer()
    to_validate = fields.Boolean()
    segment_ids = fields.One2many('operation.segment', 'order_id', 'Segment')
    repatriate_information = fields.Boolean('Repatriate Informations On Delivery Informations Tab')
    operation_type_id = fields.Many2one('project.project', compute='_compute_operation_type_id', store=True)
    can_display_redelivery = fields.Boolean(compute='_compute_can_display_delivery')
    can_display_livery_project = fields.Boolean(compute='_compute_can_display_delivery')
    can_display_to_plan = fields.Boolean(compute='_compute_can_display_delivery')
    delivery_email_to = fields.Char()
    delivery_info_task_id = fields.Many2one('project.task', 'Delivery Info', compute='compute_delivery_info_task_id')

    def compute_delivery_info_task_id(self):
        self.delivery_info_task_id = self.tasks_ids.filtered(lambda t: t.task_number == '80').id or False

    @api.depends('project_ids')
    def _compute_operation_type_id(self):
        for rec in self:
            rec.operation_type_id = rec.project_ids[0] if rec.project_ids else False

    @api.depends('operation_type_id.stage_id')
    def _compute_can_display_delivery(self):
        STAGE_REDELIVERY_PROJECT = [
            self.env.ref('choreograph_project.planning_project_stage_in_progress').id,
            self.env.ref('choreograph_project.planning_project_stage_to_deliver').id,
            self.env.ref('choreograph_project.planning_project_stage_terminated').id,
            self.env.ref('choreograph_project.planning_project_stage_presta_delivery').id,
        ]
        STAGE_DELIVERY_PROJECT = [
            self.env.ref('choreograph_project.planning_project_stage_presta_delivery').id,
            self.env.ref('choreograph_project.planning_project_stage_to_deliver').id,
        ]
        STAGE_TO_PLAN_PROJECT = [
            self.env.ref('choreograph_project.planning_project_stage_draft').id
        ]
        STAGE_TO_PLAN_PROJECT = [
            self.env.ref('choreograph_project.planning_project_stage_draft').id
        ]
        for rec in self:
            rec.can_display_redelivery = rec.operation_type_id.stage_id.id in STAGE_REDELIVERY_PROJECT if rec.operation_type_id else False
            rec.can_display_livery_project = rec.operation_type_id.stage_id.id in STAGE_DELIVERY_PROJECT if rec.operation_type_id else False
            rec.can_display_to_plan = rec.operation_type_id.stage_id.id in STAGE_TO_PLAN_PROJECT if rec.operation_type_id else False

    @api.onchange('potential_return')
    def onchange_potential_return(self):
        self.study_delivery = self.potential_return
        if self.potential_return:
            self._unarchive_task('potential_return')
            self._archive_task('study_global')
        else:
            self._archive_task('potential_return')
            self._unarchive_task('study_global')

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

    def _get_operation_task(self, task_number_list, active=True):
        for rec in self:
            if self._context.get('is_operation_generation'):
                sale_id = rec.id
            else:
                sale_id = rec.id.origin
            if sale_id:
                return self.env['project.task'].search(
                    ['&', ('display_project_id', '!=', 'False'), '|', ('sale_line_id', 'in', rec.order_line.ids),
                     ('sale_order_id', '=', sale_id), ('active', '=', active),
                     ('task_number', 'in', task_number_list)])
            return False

    def _unarchive_task(self, operation_task):
        for rec in self:
            task = rec._get_operation_task([OPERATION_TASK_NUMBER[operation_task]], False) or rec._get_operation_task([
                OPERATION_TASK_NUMBER[operation_task]], True)
            if task:
                task.write({
                    'active': True,
                })
                rec.write({
                    operation_task + '_task_id': task.id
                })
                vals = {
                    'potential_return': rec.potential_return_date,
                    'study_delivery': rec.study_delivery_date,
                    'presentation': rec.presentation_date,
                }
                if operation_task != 'study_global':
                    task.write({
                        'date_deadline': vals[operation_task]
                    })

    def _archive_task(self, operation_task):
        for rec in self:
            task = rec._get_operation_task([OPERATION_TASK_NUMBER[operation_task]], True)
            if task:
                task.write({
                    'active': False,
                })

    @api.depends('potential_return', 'study_delivery', 'presentation')
    def _compute_operation_task(self):
        for rec in self:
            rec.potential_return_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == OPERATION_TASK_NUMBER['potential_return']).id or False
            rec.study_delivery_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == OPERATION_TASK_NUMBER['study_delivery']).id or False
            rec.presentation_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == OPERATION_TASK_NUMBER['presentation']).id or False

    @api.depends('order_line')
    def get_provider_delivery_template(self):
        line_with_project = self.get_operation_product()
        if line_with_project:
            provider_template = line_with_project[0].operation_template_id.task_ids.filtered(
                lambda t: t.task_number == PROVIDER_DELIVERY_NUMBER)
            return provider_template if provider_template else False
        return False

    def archive_required_tasks(self):
        for task in self.tasks_ids.filtered(lambda t: t.task_number in REQUIRED_TASK_NUMBER.values()):
            task.active = False

    def action_generate_operation(self):
        super(SaleOrder, self).action_generate_operation()

        for project in self.order_line.mapped('project_id'):
            project.name = project.name.replace(' (TEMPLATE)', '').replace(f'{project.sale_order_id.name} - ', '')

        self.archive_required_tasks()
        provider_delivery_template = self.get_provider_delivery_template()
        if provider_delivery_template:
            self.with_context(no_create_delivery_task=True).write({
                'operation_provider_delivery_ids': [(0, 0, {
                    'delivery_date': provider_delivery_template.date_deadline,
                    'task_id': self.tasks_ids.filtered(lambda t: t.task_number == PROVIDER_DELIVERY_NUMBER).id
                })]
            })
        self.compute_task_operations()
        self._manage_task_assignation()

    def compute_task_operations(self):
        self.with_context(is_operation_generation=True).onchange_potential_return()
        self.with_context(is_operation_generation=True).onchange_study_delivery()
        self.with_context(is_operation_generation=True).onchange_presentation()

    def check_project_count(func):
        def wrapper(self):
            if len(self.project_ids) > 1:
                raise UserError(_("the SO contains several projects"))
            return func(self)
        return wrapper

    @check_project_count
    def action_redelivery(self):
        project_id = self.project_ids[0]
        redelivery_type = self.env.context.get('redelivery_type')
        if redelivery_type == 'studies':
            project_id.js_redelivery_studies()
        else:
            project_id.js_redelivery_prod()

    @check_project_count
    def action_livery_project(self):
        project_id = self.project_ids[0]
        if project_id._is_compaign():
            return project_id.livery_project_compaign()
        # return project_id.livery_project()
        return self.action_send_delivery_email()

    @check_project_count
    def action_to_plan(self):
        project_id = self.project_ids[0]
        return project_id.action_to_plan()

    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        self._update_date_deadline(vals)
        self._check_info_validated(vals)
        return res

    @api.model
    def create(self, vals):
        vals['is_info_validated'] = False
        vals['email_is_info_validated'] = False
        order_id = super(SaleOrder, self).create(vals)
        if self.env.context.get('create_project_from_template', False):
            project = self.env['project.project'].browse(self.env.context.get('operation_id', False)).exists()
            if project:
                project.initialize_order(order_id)
                order_id.write({
                    'project_id': project.id,
                    'show_operation_generation_button': False
                })
                order_id.archive_required_tasks()
                order_id.compute_task_operations()
        return order_id

    def _update_date_deadline(self, vals):
        for rec in self:
            if vals.get('commitment_date'):
                tz = timezone(self.env.user.tz or self.env.context.get('tz') or 'UTC')
                date = utc.localize(rec.commitment_date).astimezone(tz)
                rec.tasks_ids.filtered(lambda t: t.task_number in ['65', '40', '85', '90', '45', '50', '25', '30', '35']).write({
                    'date_deadline': date,
                })
                rec.tasks_ids.filtered(lambda t: t.task_number in ['80']).write({
                    'date_deadline': date - relativedelta(days=2),
                })
            if vals.get('potential_return_date') and rec.potential_return_task_id:
                rec.potential_return_task_id.date_deadline = rec.potential_return_date
            if vals.get('study_delivery_date') and rec.study_delivery_task_id:
                rec.study_delivery_task_id.date_deadline = rec.study_delivery_date
            if vals.get('presentation_date') and rec.presentation_task_id:
                rec.presentation_task_id.date_deadline = rec.presentation_date

    def _check_info_validated(self, vals):
        for rec in self:
            if vals.get('is_info_validated'):
                rec._get_operation_task(['50', '55', '60']).update_task_stage(TODO_TASK_STAGE)
            if vals.get('email_is_info_validated'):
                rec._get_operation_task(['45', '55', '60']).update_task_stage(TODO_TASK_STAGE)

    @api.onchange('is_info_validated')
    def _onchange_sms_info_validated(self):
        if self.id.origin:
            for rec in self:
                rec.check_operation_exists()
                rec.check_campaign_tasks_exist(SMS_TASK_NUMBER)
                rec.check_task_stage_number(self._get_operation_task([SMS_TASK_NUMBER]).stage_id.stage_number)

    @api.onchange('email_is_info_validated')
    def _onchange_email_info_validated(self):
        if self.id.origin:
            for rec in self:
                rec.check_operation_exists()
                rec.check_campaign_tasks_exist(EMAIL_TASK_NUMBER)
                rec.check_task_stage_number(self._get_operation_task([EMAIL_TASK_NUMBER]).stage_id.stage_number)

    def check_operation_exists(self):
        if not self.project_ids:
            raise ValidationError(_('You must already generate the operation to launch the tasks on the campaigns'))

    def check_campaign_tasks_exist(self, task_number):
        for rec in self:
            if not rec._get_operation_task([task_number]):
                raise ValidationError(
                    _('You can\'t check this field, the task {0} doesn\'t exist in the operation').format(_(CAMPAIGN_TASK_NAME[task_number])))

    def check_task_stage_number(self, number=''):
        if number != CHECK_TASK_STAGE_NUMBER:
            raise ValidationError(_('The task is in progress, you can\'t check/uncheck this field'))

    def action_view_task(self):
        action = super().action_view_task()
        project_id = self.env['project.project'].browse(action['context'].get('default_project_id', False)).exists()
        if project_id:
            action['context'].update({'default_type_of_project': project_id.type_of_project})
        return action

    def _manage_task_assignation(self):
        self.ensure_one()
        if not self.partner_id.role_ids:
            return False
        for task in self.project_ids.task_ids.filtered(lambda tsk: tsk.role_id):
            roles = self.partner_id.role_ids.filtered(lambda pr: pr.role_id == task.role_id)
            if not roles:
                continue
            task.write({'user_ids': [(6, 0, roles.mapped('user_ids').ids)]})
        return True

    def action_send_delivery_email(self):
        composer_form_view_id = self.env.ref('mail.email_compose_message_wizard_form')
        template_id = self.env.ref('choreograph_sale_project.email_template_choreograph_delivery')
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'view_id': composer_form_view_id.id,
            'target': 'new',
            'context': {
                'default_composition_mode': 'comment',
                'default_email_layout_xmlid': 'mail.mail_notification_light',
                'default_res_id': self.id,
                'default_model': 'sale.order',
                'default_use_template': bool(template_id),
                'default_template_id': template_id.id,
                'website_sale_send_recovery_email': True,
                'active_ids': self.ids,
                'operation_email_process': True,
            },
        }
