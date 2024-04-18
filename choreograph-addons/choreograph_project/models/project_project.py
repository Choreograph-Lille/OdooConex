# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import html_escape
from odoo.tools.misc import format_date
from datetime import date, datetime

state_done = {'kanban_state': 'done'}
state_normal = {'kanban_state': 'normal'}

WAITING_TASK_STAGE = '10'
TODO_TASK_STAGE = '15'
WAITING_FILE_TASK_STAGE = '20'
FILE_RECEIVED_TASK_STAGE = '25'
WAITING_DETAILS_TASK_STAGE = '30'
IN_PREPARATION_TASK_STAGE = '40'
IN_PROGRESS_TASK_STAGE = '50'
WAITING_QTY_TASK_STAGE = '60'
BAT_CLIENT_TASK_STAGE = '70'
TERMINATED_TASK_STAGE = '80'
CANCELED_TASK_STAGE = '90'

STUDIES_DELIVERY_TASK = '30'
PROJECT_NAME_TASK = '20'
DELIVERY_INFOS_TASK = '80'
FULLFILLEMENT_TASK = '85'

DRAFT_PROJECT_STAGE = '10'
PLANIFIED_PROJECT_STAGE = '20'
IN_PROGRESS_PROJECT_STAGE = '30'
DELIVERY_PRESTA_PROJECT_STAGE = '40'
DELIVERY_PROJECT_STAGE = '50'
LIVERY_PROJECT_STAGE = '60'
ROUTING_PROJECT_STAGE = '70'
EXTRACTION_PROJECT_STAGE = '80'
TERMINATED_PROJECT_STAGE = '90'
CANCELED_PROJECT_STAGE = '100'
TEMPLATE_PROJECT_STAGE = '140'

DELIVERY_TASK_NUMBER = 30
TYPE_OF_PROJECT = [
    ('standard', 'standard'),
    ('operation', 'operation')
]


def filter_by_type_of_project(func):
    def wrapper(self, stages, domain, order):
        type_of_project = self._context.get('default_type_of_project', 'standard')
        result = func(self, stages, domain, order)
        return result.filtered(lambda item: item.type_of_project == type_of_project)

    return wrapper


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    @filter_by_type_of_project
    def _read_group_stage_ids(self, stages, domain, order):
        return super(ProjectProject, self)._read_group_stage_ids(stages, domain, order)

    type_of_project = fields.Selection(TYPE_OF_PROJECT, default='standard')
    code_sequence = fields.Char()
    code = fields.Char()
    display_name = fields.Char(string='Display Name', automatic=True, compute='_compute_display_name', store=False)

    def get_waiting_task_stage(self):
        todo_stage_id = self.type_ids.filtered(lambda t: t.stage_number == TODO_TASK_STAGE)
        if todo_stage_id:
            return {'stage_id': todo_stage_id.id, 'kanban_state': 'normal'}
        waiting_stage_id = self.type_ids.filtered(lambda t: t.stage_number == WAITING_TASK_STAGE)
        if waiting_stage_id:
            return {'stage_id': waiting_stage_id.id, 'kanban_state': 'done'}
        return {'kanban_state': 'normal'}

    def update_task_to_waiting(self, task_number):
        values = self.get_waiting_task_stage()
        self.task_ids.filtered(lambda t: int(t.task_number) > task_number).write(values)

    def js_redelivery_studies(self):
        studies_delivery_task_id = self.task_ids.filtered(lambda t: t.task_number == STUDIES_DELIVERY_TASK)
        project_name_task_id = self.task_ids.filtered(lambda t: t.task_number == PROJECT_NAME_TASK)
        main_task_id = studies_delivery_task_id or project_name_task_id
        if main_task_id:
            values = self.get_waiting_task_stage()
            main_task_id.write(values)
            self.update_task_to_waiting(DELIVERY_TASK_NUMBER)
        self.update_project_stage(IN_PROGRESS_PROJECT_STAGE)

    def js_redelivery_prod(self):
        delivery_info_task_id = self.task_ids.filtered(lambda t: t.task_number == DELIVERY_INFOS_TASK)
        fullfillement_task_id = self.task_ids.filtered(lambda t: t.task_number == FULLFILLEMENT_TASK)
        if delivery_info_task_id:
            delivery_info_task_id.write(state_done)
        if fullfillement_task_id:
            fullfillement_task_id.write(state_normal)
        self.update_project_stage(IN_PROGRESS_PROJECT_STAGE)

    def _find_task_by_task_number(self, task_number: str):
        return self.task_ids.filtered(lambda task: task.task_number == task_number)

    def _get_task_stage_number_by_task_number(self, task_number: str):
        task_id = self._find_task_by_task_number(task_number)
        return task_id.stage_number if task_id else False

    def _update_task_stage(self, task_number: str, stage_number: str):
        task_id = self._find_task_by_task_number(task_number)
        if task_id:
            task_id.update_task_stage(stage_number)

    def livery_project(self):
        if self.stage_id.stage_number == '40':
            self._update_task_stage('80', TODO_TASK_STAGE)
            self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_in_progress').id})
        elif self.stage_id.stage_number == '50':
            self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_livery').id})
        return True

    def update_project_stage(self, number):
        project_stage_id = self.env['project.project.stage'].search([('stage_number', '=', number)], limit=1)
        if project_stage_id:
            self.write({'stage_id': project_stage_id.id})

    @api.model_create_multi
    def create(self, vals_list):
        project_task_obj = self.env['project.task']
        project_project_obj = self.env['project.project']
        sequence_obj = self.env['ir.sequence']
        for vals in vals_list:
            if self._context.get('is_operation_generation') or self._context.get(
                    'default_type_of_project') == 'operation':
                types = project_task_obj.get_operation_project_task_type()
                name_seq = sequence_obj.next_by_code('project.project.operation')
                project_name = False
                if vals.get('project_template_id', False):
                    project_name = project_project_obj.browse(vals['project_template_id']).name
                    project_name = project_name.replace('(TEMPLATE)', '').replace('(COPY)', '')
                vals.update({
                    'type_of_project': 'operation',
                    'code_sequence': name_seq,
                    'stage_id': self.env.ref('choreograph_project.planning_project_stage_draft',
                                             raise_if_not_found=False).id,
                    'type_ids': [(6, 0, types.ids)],
                    'user_id': self._context.get('user_id', vals.get('user_id')),
                    'name': '%s - %s' % (name_seq, vals.get('name') or project_name)
                })
        return super(ProjectProject, self).create(vals_list)

    def action_view_tasks(self):
        action = super().action_view_tasks()
        action['context'].update({'default_type_of_project': self.type_of_project})
        return action

    def action_to_plan(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_planified').id})

    @api.model
    def _get_fields_to_track_notification(self):
        SaleOrder = self.env['sale.order']
        return SaleOrder.get_operation_fields() + SaleOrder.get_sms_campaign_field() + SaleOrder.get_email_campaign_field()

    def write(self, values):
        res = super().write(values)
        if "stage_id" in values and values["stage_id"] == self.env.ref(
                'choreograph_project.planning_project_stage_planified').id:
            self._notify_planned_operation()
        if "stage_id" in values and values["stage_id"] == self.env.ref(
                'choreograph_project.planning_project_stage_canceled').id:
            self._notify_canceled_operation()
        return res

    def _notify_project_change(self, body):
        self.ensure_one()
        self.message_post(
            body=body,
            partner_ids=self.message_follower_ids.mapped('partner_id').ids,
        )

    def notify_field_change(self, field_list):
        for project in self:
            body = _("%s changed") % project.display_name
            body += "<ul>"
            for f in field_list:
                body += f"<li>{html_escape(f._description_string(self.env))}</li>"
            body += "</ul>"
            project._notify_project_change(body)

    def _notify_planned_operation(self):
        for project in self:
            self._notify_project_change(
                body=(project._get_body_message_planned_operation(_("The operations %s has been Planned") % self.name)))

    def _notify_canceled_operation(self):
        for project in self:
            self._notify_project_change(
                body=(project._get_body_message_planned_operation(_("The operations %s has been Canceled") % self.name)))

    def _get_body_message_planned_operation(self, title):
        self.ensure_one()
        body_msg = title
        field_to_notify = self._field_to_notify()
        for key, value in field_to_notify.items():
            if not value[0]:
                field_value = _("<span class='text-muted'><i>Empty</i></span>")
            elif isinstance(value[0], (date, datetime)):
                field_value = format_date(self.env, value[0], date_format="dd/MM/yyyy")
            else:
                field_value = value[0]
            body_msg += f"<li>{field_value} <i>({value[1]})</i></li>"
        body_msg += _(
            "</ul><p> You can access to this document: <a href='#' data-oe-model='project.project' data-oe-id='%s'>%s</a></p>") % (
                        self.id, field_to_notify['operation'][0])
        return body_msg

    def _field_to_notify(self):
        self.ensure_one()
        split_name = self.name.split('-')
        return {
            "operation": (split_name[0] if len(split_name) > 0 else "", _('Operation')),
            "type": (split_name[1] if len(split_name) > 1 else "", _('Type')),
            "customer": (self.sale_order_id.partner_id.display_name, _('Customer')),
            "order_id": (self.sale_order_id.display_name, _('Sale order')),
            "base": (self.sale_order_id.related_base.display_name, _('Base')),
            "commercial": (self.sale_order_id.user_id.display_name, _('Commercial')),
            "study_delivery_date": (self.sale_order_id.study_delivery_date, _('Study delivery date')),
            "commitment_date": (self.sale_order_id.study_delivery_date, _('Customer delivery date')),
        }

    def name_get(self):
        result = []
        for project in self:
            name = project.name
            if project.partner_id:
                name += " - %s" % project.partner_id.name
            result.append((project.id, name))
        return result

    def _creation_message(self):
        if self.type_of_project == 'operation':
            return self._get_body_message_planned_operation(_('Operation created'))
        return super()._creation_message()
