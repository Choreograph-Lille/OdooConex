# -*- coding: utf-8 -*-

from datetime import date
from pytz import timezone, utc

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from odoo.addons.choreograph_sale.models.sale_order import REQUIRED_TASK_NUMBER
from odoo.addons.choreograph_project.models.project_project import TODO_TASK_STAGE, WAITING_FILE_TASK_STAGE

PROVIDER_DELIVERY_NUMBER = '75'
SMS_TASK_NUMBER = '50'
EMAIL_TASK_NUMBER = '45'
BAT_FILE_WITNESS_TASK_NUMBER = '55'
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

    potential_return = fields.Boolean(copy=False, tracking=True)
    return_production_potential = fields.Boolean('Return of production potential', tracking=True)
    study_delivery = fields.Boolean(copy=False, tracking=True)
    presentation = fields.Boolean(copy=False, tracking=True)

    potential_return_task_id = fields.Many2one(
        'project.task', 'Potential Return Task', copy=False, tracking=True)
    study_delivery_task_id = fields.Many2one('project.task', 'Study Delivery Task', copy=False, tracking=True)
    presentation_task_id = fields.Many2one('project.task', 'Presentation Task', copy=False, tracking=True)
    study_global_task_id = fields.Many2one('project.task', 'Study Global Task', copy=False, tracking=True)

    potential_return_date = fields.Date(copy=False, tracking=True)
    study_delivery_date = fields.Date(copy=False, tracking=True)
    presta_delivery_date = fields.Date(copy=False, tracking=True)
    presentation_date = fields.Date(copy=False, tracking=True)
    return_production_potential_date = fields.Date('Date of return of production potential', tracking=True)
    operation_code = fields.Char(compute='compute_operation_code', store=True)

    operation_provider_delivery_ids = fields.One2many('operation.provider.delivery', 'order_id', 'Provider Delivery')
    comment = fields.Text(tracking=True)
    quantity_to_deliver = fields.Integer(tracking=True)
    to_validate = fields.Boolean(tracking=True)
    segment_ids = fields.One2many('operation.segment', 'order_id', 'Segment')
    repatriate_information = fields.Boolean('Repatriate Informations On Delivery Informations Tab', tracking=True)
    operation_type_id = fields.Many2one(
        'project.project', compute='_compute_operation_type_id', store=True, tracking=True)
    can_display_redelivery = fields.Boolean(compute='_compute_can_display_delivery')
    can_display_livery_project = fields.Boolean(compute='_compute_can_display_delivery')
    can_display_to_plan = fields.Boolean(compute='_compute_can_display_delivery')
    delivery_email_to = fields.Char(tracking=True)
    delivery_info_task_id = fields.Many2one('project.task', 'Delivery Info', compute='compute_delivery_info_tasks')
    presta_delivery_info_task_id = fields.Many2one(
        'project.task', 'Presta Delivery Info', compute='compute_delivery_info_tasks')
    has_enrichment_email_op = fields.Boolean(compute='_compute_has_email_op')
    has_prospection_email_op = fields.Boolean(compute='_compute_has_email_op')

    @api.model
    def get_operation_fields(self):
        return [
            self.env.ref('choreograph_sale_project.field_sale_order__potential_return').id,
            self.env.ref('choreograph_sale_project.field_sale_order__return_production_potential').id,
            self.env.ref('choreograph_sale_project.field_sale_order__study_delivery').id,
            self.env.ref('choreograph_sale_project.field_sale_order__presentation').id,
            self.env.ref('choreograph_sale_project.field_sale_order__potential_return_task_id').id,
            self.env.ref('choreograph_sale_project.field_sale_order__study_delivery_task_id').id,
            self.env.ref('choreograph_sale_project.field_sale_order__presentation_task_id').id,
            self.env.ref('choreograph_sale_project.field_sale_order__study_global_task_id').id,
            self.env.ref('choreograph_sale_project.field_sale_order__potential_return_date').id,
            self.env.ref('choreograph_sale_project.field_sale_order__study_delivery_date').id,
            self.env.ref('choreograph_sale_project.field_sale_order__presta_delivery_date').id,
            self.env.ref('choreograph_sale_project.field_sale_order__presentation_date').id,
            self.env.ref('choreograph_sale_project.field_sale_order__return_production_potential_date').id,
            self.env.ref('choreograph_sale_project.field_sale_order__comment').id,
            self.env.ref('choreograph_sale_project.field_sale_order__quantity_to_deliver').id,
            self.env.ref('choreograph_sale_project.field_sale_order__to_validate').id,
            self.env.ref('choreograph_sale_project.field_sale_order__repatriate_information').id,
            self.env.ref('choreograph_sale_project.field_sale_order__delivery_email_to').id,
            self.env.ref('choreograph_sale_project.field_sale_order__delivery_info_task_id').id,
            self.env.ref('choreograph_sale_project.field_sale_order__presta_delivery_info_task_id').id,
        ]

    @api.model
    def get_mail_field_to_operation(self):
        result = super().get_mail_field_to_operation()
        operation_field = self.get_operation_fields()
        result.extend(operation_field)
        return result

    def compute_delivery_info_tasks(self):
        self.delivery_info_task_id = self.tasks_ids.filtered(lambda t: t.task_number == '80').id or False
        self.presta_delivery_info_task_id = self.tasks_ids.filtered(lambda t: t.task_number == '70').id or False

    @api.depends('project_ids')
    def _compute_operation_type_id(self):
        for rec in self:
            rec.operation_type_id = rec.project_ids[0] if rec.project_ids else False

    def _compute_has_email_op(self):
        for rec in self:
            rec.has_enrichment_email_op = True if rec.operation_code == 'ENR_EMAIL' else False
            rec.has_prospection_email_op = True if rec.operation_code == 'PREMAIL' else False

    @api.depends('operation_type_id.stage_id', 'project_id')
    def _compute_can_display_delivery(self):
        STAGE_REDELIVERY_PROJECT = [
            self.env.ref('choreograph_project.planning_project_stage_in_progress', raise_if_not_found=False).id,
            self.env.ref('choreograph_project.planning_project_stage_to_deliver', raise_if_not_found=False).id,
            self.env.ref('choreograph_project.planning_project_stage_terminated', raise_if_not_found=False).id,
            self.env.ref('choreograph_project.planning_project_stage_presta_delivery', raise_if_not_found=False).id,
        ]
        STAGE_DELIVERY_PROJECT = [
            self.env.ref('choreograph_project.planning_project_stage_presta_delivery', raise_if_not_found=False).id,
            self.env.ref('choreograph_project.planning_project_stage_to_deliver', raise_if_not_found=False).id,
        ]
        STAGE_TO_PLAN_PROJECT = [
            self.env.ref('choreograph_project.planning_project_stage_draft', raise_if_not_found=False).id
        ]
        STAGE_TO_PLAN_PROJECT = [
            self.env.ref('choreograph_project.planning_project_stage_draft', raise_if_not_found=False).id
        ]
        for rec in self:
            rec.can_display_redelivery = rec.operation_type_id.stage_id.id in STAGE_REDELIVERY_PROJECT if rec.operation_type_id else False
            rec.can_display_livery_project = rec.operation_type_id.stage_id.id in STAGE_DELIVERY_PROJECT if rec.operation_type_id else False
            operation_id = rec.operation_type_id or rec.project_id
            rec.can_display_to_plan = operation_id.stage_id.id in STAGE_TO_PLAN_PROJECT if operation_id else False

    def update_potential_return(self):
        if self.potential_return:
            self._unarchive_task('potential_return')
            self._unarchive_task('study_delivery')
            self._archive_task('study_global')
            self.update_operation_task_comment()
        else:
            self._archive_task('potential_return')
            self._archive_task('study_delivery')
            self._unarchive_task('study_global')

    def update_presentation(self):
        if self.presentation:
            self._unarchive_task('presentation')
        else:
            self._archive_task('presentation')

    def _get_operation_task(self, task_number_list, active=True):
        # return self.project_ids.mapped('task_ids').filtered(lambda item: item.task_number in task_number_list and item.active == active)
        return self.env['project.task'].search([
            ('project_id', 'in', self.project_ids.ids),
            ('task_number', 'in', task_number_list),
            ('active', '=', active)])

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
                # CNXMIG-102
                if rec.project_ids and rec.project_ids[0].stage_id.id == self.env.ref('choreograph_project.planning_project_stage_planified').id and operation_task == 'potential_return':
                    rec.update_task_stage_to_15(task)

    def _archive_task(self, operation_task):
        for rec in self:
            task = rec._get_operation_task([OPERATION_TASK_NUMBER[operation_task]], True)
            if task:
                task.write({
                    'active': False,
                })

    def update_task_stage_to_15(self, task=False):
        to_do_stage = self.env.ref('choreograph_project.project_task_type_to_do', raise_if_not_found=False)
        task.write({
            'stage_id': to_do_stage.id
        })

    @api.depends('potential_return', 'presentation')
    def _compute_operation_task(self):
        for rec in self:
            rec.potential_return_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == OPERATION_TASK_NUMBER['potential_return']).id
            rec.study_delivery_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == OPERATION_TASK_NUMBER['study_delivery']).id
            rec.presentation_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == OPERATION_TASK_NUMBER['presentation']).id
            rec.study_global_task_id = rec.tasks_ids.filtered(
                lambda t: t.task_number == OPERATION_TASK_NUMBER['study_global']).id

    def get_provider_delivery_template(self, project=False):
        line_with_project = self.get_operation_product()
        operation_template = False
        if line_with_project:
            operation_template = line_with_project[0].operation_template_id
        elif project:
            operation_template = project

        return operation_template.task_ids.filtered(lambda t: t.task_number == PROVIDER_DELIVERY_NUMBER) if operation_template else False

    # def archive_required_tasks(self):
    #     for task in self.tasks_ids.filtered(lambda t: t.task_number in REQUIRED_TASK_NUMBER.values()):
    #         task.active = False

    def action_generate_operation(self):
        super(SaleOrder, self).action_generate_operation()

        for project in self.order_line.mapped('project_id'):
            project.name = project.name.replace(' (TEMPLATE)', '').replace(f'{project.sale_order_id.name} - ', '')

        # self.archive_required_tasks()
        self._manage_task_assignation()
        self.compute_task_operations()
        self.initiate_provider_delivery(self.project_ids[0])
        self.with_context(is_operation_generation=True, user_id=self.user_id.id)._update_date_deadline()

    def initiate_provider_delivery(self, project=False):
        provider_delivery_template = self.get_provider_delivery_template(project)
        if provider_delivery_template and project:
            self.write({
                'operation_provider_delivery_ids': [(0, 0, {
                    'task_id': project.task_ids.filtered(lambda t: t.task_number == PROVIDER_DELIVERY_NUMBER).id
                })]
            })

    def compute_task_operations(self):
        self.with_context(is_operation_generation=True).update_potential_return()
        self.with_context(is_operation_generation=True).update_presentation()

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
        for rec in self:
            if any(date in vals for date in ['commitment_date', 'potential_return_date', 'study_delivery_date',
                                             'presentation_date', 'return_production_potential_date',
                                             'operation_provider_delivery_ids', 'bat_desired_date']):
                rec._update_date_deadline(vals)
            rec._check_info_validated(vals)
            if vals.get('is_info_validated', False) or any(field in vals for field in [
                'po_number',
                'campaign_name',
                'sms_personalization',
                'sms_personalization_text',
                'sms_comment',
                'bat_internal',
                'desired_finished_volume',
                'sender',
            ]) and rec.is_info_validated:
                rec.update_task_sms_campaign()
                rec.update_task_campaign_90('sms')
            if vals.get('email_is_info_validated', False) or any(field in vals for field in [
                'email_reception_date',
                'email_routing_date',
                'email_reception_location',
                'email_routing_end_date',
                'email_desired_finished_volume',
                'email_sender',
                'email_personalization',
                'email_personalization_text',
                'is_preheader_available',
                'is_preheader_available_text',
                'ab_test',
                'ab_test_text',
                'email_comment',
                'email_bat_internal',
                'bat_desired_date',
                'email_witness_file_name',
                'livedata_po_number',
                'email_campaign_name',
                'email_comment',
            ]) and rec.email_is_info_validated:
                rec.update_task_email_campaign()
                rec.update_task_campaign_90('email')
                rec.update_task_bat_file_witness()

            if any(field in vals for field in ['repatriate_information', 'segment_ids']):
                if vals.get('repatriate_information') or rec.repatriate_information:
                    rec.repatriate_quantity_information_on_task()
            if 'quantity_to_deliver' in vals:
                rec.repatriate_volume_on_task()
            if 'repatriate_information' in vals and not vals.get('repatriate_information'):
                rec.reset_quantity_information_on_task()

            if 'potential_return' in vals:
                rec.update_potential_return()
            if 'presentation' in vals:
                rec.update_presentation()
            if 'comment' in vals:
                rec.update_operation_task_comment()
            if 'bat_from' in vals:
                rec.update_task_bat_from(rec.bat_from.id)
            if 'email_bat_from' in vals:
                rec.update_task_bat_from(rec.email_bat_from.id)
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
                    'project_ids': [(4, project.id)],
                    'show_operation_generation_button': False
                })
                order_id.compute_operation_code()
                order_id.compute_task_operations()
                order_id.initiate_provider_delivery(project)
                order_id.with_context(is_operation_generation=True)._update_date_deadline(vals)
                order_id._manage_task_assignation()
        return order_id

    def update_task_bat_from(self, value=''):
        self.tasks_ids.write({
            'bat_from': value
        })

    def update_operation_task_comment(self):
        for rec in self:
            rec._get_operation_task(['25', '30', '40']).write({
                'comment': rec.comment
            })

    def repatriate_quantity_information_on_task(self):
        self.tasks_ids.filtered(lambda t: t.task_number in [
                                '20', '25', '30', '85', '80']).repatriate_quantity_information()

    def repatriate_volume_on_task(self):
        self.tasks_ids.filtered(lambda t: t.task_number in ['80']).repatriate_volume()

    def reset_quantity_information_on_task(self):
        self.tasks_ids.filtered(lambda t: t.task_number in ['80']).write({
            'segment_ids': [(6, 0, [])],
            'task_segment_ids': [(6, 0, [])],
        })

    def get_date_tz(self, datetime_to_convert):
        tz = timezone(self.env.user.tz or self.env.context.get('tz') or 'UTC')
        tz_date = utc.localize(datetime_to_convert).astimezone(tz)
        return tz_date

    def _update_date_deadline(self, vals={}):
        for rec in self:
            values = []
            is_operation_generation = self._context.get('is_operation_generation')
            if (is_operation_generation or vals.get('commitment_date')) and rec.commitment_date:
                tz_date = rec.get_date_tz(rec.commitment_date)
                values.extend([(rec._get_operation_task(['85']), {'date_deadline': tz_date}),
                              (rec._get_operation_task(['65', '80']), {'date_deadline': tz_date - relativedelta(days=2)})])

            if (is_operation_generation or vals.get('potential_return_date')) and rec.potential_return_task_id:
                values.append((rec.potential_return_task_id, {'date_deadline': rec.potential_return_date}))

            if is_operation_generation or vals.get('study_delivery_date'):
                task = rec.study_delivery_task_id if rec.potential_return else rec.study_global_task_id
                values.append((task, {'date_deadline': rec.study_delivery_date}))

            if (is_operation_generation or vals.get('presentation_date')) and rec.presentation_task_id:
                values.append((rec.presentation_task_id, {'date_deadline': rec.presentation_date}))

            if is_operation_generation or vals.get('return_production_potential_date'):
                values.append((rec._get_operation_task(['40'], True), {
                              'date_deadline': rec.return_production_potential_date}))

            if is_operation_generation or vals.get('operation_provider_delivery_ids') or vals.get('commitment_date') or vals.get('is_info_validated', False) or vals.get('email_is_info_validated', False):
                values.extend([(rec._get_operation_task(['45', '50'], True), {'delivery_date': rec.operation_provider_delivery_ids[0].delivery_date if rec.operation_code in [
                              'ENR_EMAIL', 'ENR_SMS'] and rec.operation_provider_delivery_ids else rec.get_date_tz(rec.commitment_date)})])

            if (is_operation_generation or vals.get('operation_provider_delivery_ids')) and rec.operation_provider_delivery_ids:
                values.extend([(rec._get_operation_task(['60', '70'], True), {
                              'date_deadline': rec.operation_provider_delivery_ids[0].delivery_date})])

            if is_operation_generation or vals.get('bat_desired_date'):
                values.append((rec._get_operation_task(['55'], True), {'date_deadline': rec.bat_desired_date}))

            rec.update_date_deadline(values)

    def update_date_deadline(self, values):
        """
        Update date_deadline for tasks
        :param values: list of tuple: (task to update, values to update)
        :return:
        """
        for task, value in values:
            task.write(value)

    def update_optout_link(self, value=''):
        for rec in self:
            rec.optout_link = value
            rec.update_tasks({'optout_link': value}, EMAIL_TASK_NUMBER)

    def _check_info_validated(self, vals):
        for rec in self:
            if vals.get('is_info_validated'):
                rec._get_operation_task(['50', '55', '60']).update_task_stage(TODO_TASK_STAGE)
            if vals.get('email_is_info_validated'):
                tasks = ['45', '60']
                if self.has_prospection_email_op:
                    tasks.append('55')
                rec._get_operation_task(tasks).update_task_stage(TODO_TASK_STAGE)

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

    @api.model
    def update_tasks(self, values, task_number):
        task_id = self._get_operation_task([task_number])
        if task_id:
            task_id.write(values)

    def update_task_email_campaign(self):
        values_list = [
            ('reception_date', 'email_reception_date'),
            ('routing_date', 'email_routing_date'),
            ('reception_location', 'email_reception_location'),
            ('routing_end_date', 'email_routing_end_date'),
            ('desired_finished_volume', 'email_desired_finished_volume'),
            ('sender', 'email_sender'),
            ('personalization', 'email_personalization'),
            ('personalization_text', 'email_personalization_text'),
            ('is_preheader_available', 'is_preheader_available'),
            ('is_preheader_available_text', 'is_preheader_available_text'),
            ('ab_test', 'ab_test'),
            ('ab_test_text', 'ab_test_text'),
            ('comment', 'email_comment'),
            ('bat_internal', 'email_bat_internal'),
            ('bat_desired_date', 'bat_desired_date'),
            ('witness_file_name', 'email_witness_file_name'),
            ('po_livedata_number', 'livedata_po_number'),
            ('campaign_name', 'email_campaign_name'),
            ('comment', 'email_comment'),
        ]
        values = {task_key: self[so_key] for task_key, so_key in values_list}
        values.update({
            'bat_from': self.email_bat_from.id if self.email_bat_from else None,
        })
        self.update_tasks(values, EMAIL_TASK_NUMBER)

    def update_task_bat_file_witness(self):
        values_list = [
            ('bat_internal', 'email_bat_internal'),
            ('witness_file_name', 'email_witness_file_name'),
        ]
        values = {task_key: self[so_key] for task_key, so_key in values_list}
        values.update({'bat_from': self.email_bat_from.id if self.email_bat_from else None})
        self.update_tasks(values, BAT_FILE_WITNESS_TASK_NUMBER)

    def update_task_sms_campaign(self):
        values_list = [
            ('po_livedata_number', 'po_number'),
            ('campaign_name', 'campaign_name'),
            ('personalization', 'sms_personalization'),
            ('personalization_text', 'sms_personalization_text'),
            ('comment', 'sms_comment'),
            ('bat_internal', 'bat_internal'),
            ('desired_finished_volume', 'desired_finished_volume'),
            ('sender', 'sender'),
        ]
        values = {task_key: self[so_key] for task_key, so_key in values_list}
        values.update({
            'user_ids': [(4, self.user_id.id)],
        })
        self.update_tasks(values, SMS_TASK_NUMBER)

    def update_task_campaign_90(self, type=''):
        vals = {}
        if type == 'sms':
            vals = {
                'start_date': self.routing_date,
                'desired_finished_volume': self.desired_finished_volume,
                'date_deadline': self.routing_end_date + relativedelta(days=5),
            }
        elif type == 'email':
            vals = {
                'start_date': self.email_routing_date,
                'desired_finished_volume': self.email_desired_finished_volume,
                'date_deadline': self.email_routing_end_date + relativedelta(days=5) if self.email_routing_end_date else False,
            }
        self.update_tasks(vals, '90')

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
        action['context'].pop('search_default_sale_order_id')
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
        self.ensure_one()
        email_to = self._get_operation_task([80]).provider_delivery_address
        if email_to:
            self.env['res.partner'].sudo().find_or_create(email_to)
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

    def action_create_task_from_condition(self):
        super().action_create_task_from_condition()
        project_id = self.project_ids[0] if self.project_ids else False
        if project_id and project_id.stage_id != self.env.ref('choreograph_project.planning_project_stage_draft'):
            task_draft_stage_id = self.env.ref('choreograph_project.project_task_type_draft')
            for condition_id in self.operation_condition_ids.filtered(lambda item: item.task_id.stage_id == task_draft_stage_id):
                condition_id.task_id.update_task_stage(WAITING_FILE_TASK_STAGE)
                # if condition_id.task_id.task_number in ('5', '10', '15'):
                #     project_id._update_task_stage(condition_id.task_id.task_number, WAITING_FILE_TASK_STAGE)
                # elif condition_id.task_id.task_number in ('20', '25', '35'):
                #     project_id._update_task_stage(condition_id.task_id.task_number, TODO_TASK_STAGE)

    @api.depends('project_ids')
    def compute_operation_code(self):
        self.operation_code = self.project_ids[0].code if self.project_ids else ''

    @api.onchange('segment_ids')
    def onchange_segment_sequence(self):
        for rec in self:
            for i, l in enumerate(rec.segment_ids):
                l.segment_number = i + 1
