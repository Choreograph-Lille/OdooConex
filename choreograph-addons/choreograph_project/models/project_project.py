from datetime import timedelta

from odoo import api, fields, models

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
        return super()._read_group_stage_ids(stages, domain, order)

    type_of_project = fields.Selection(
        TYPE_OF_PROJECT, default='standard', required=True, compute='_compute_type_of_project', store=True, readonly=False)

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
        delivery_task_number = '0'
        if self.stage_id.stage_number == '40':
            self._update_task_stage('80', '15')
            self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_in_progress').id})
            delivery_task_number = '75'
        elif self.stage_id.stage_number == '50':
            self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_livery').id})
            # if not self.task_ids.filtered(lambda task: task.task_number == '90'):
            #     self._update_95_to_15_with_commitment_date()
            delivery_task_number = '85'
        self.sale_order_id.delivery_email_to = self.task_ids.filtered(
            lambda t: t.task_number == delivery_task_number).provider_delivery_address
        return self.sale_order_id.action_send_delivery_email(completed_task=delivery_task_number)

    # def _update_95_to_15_with_commitment_date(self):
    #     task_95 = self.task_ids.filtered(lambda task: task.task_number == '95')
    #     if task_95:
    #         task_stage_id = self.env['project.task.type'].search([('stage_number', '=', TODO_TASK_STAGE)], limit=1)
    #         values = {}
    #         if task_stage_id:
    #             values.update({'stage_id': task_stage_id.id})
    #         if self.sale_order_id.commitment_date:
    #             values.update({'date_deadline': self.sale_order_id.commitment_date + timedelta(days=15)})
    #         task_95.write(values)

    def update_project_stage(self, number):
        project_stage_id = self.env['project.project.stage'].search([('stage_number', '=', number)], limit=1)
        if project_stage_id:
            self.write({'stage_id': project_stage_id.id})

    @api.depends('sale_order_id')
    def _compute_type_of_project(self):
        for rec in self:
            rec.type_of_project = 'operation' if rec.sale_order_id else 'standard'

    @api.model
    def create(self, values):
        if self._context.get('is_operation_generation'):
            type_ids = self.env['project.task'].get_operation_project_task_type()
            values.update({
                'type_of_project': 'operation',
                'stage_id': self.env.ref('choreograph_project.planning_project_stage_draft').id,
                'type_ids': [(6, 0, type_ids.ids)]
            })
        project_id = super().create(values)
        return project_id

    def action_view_tasks(self):
        action = super().action_view_tasks()
        action['context'].update({'default_type_of_project': self.type_of_project})
        return action

    def action_to_plan(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_planified').id})
