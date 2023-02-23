from odoo import api, fields, models
from ..models import WAITING_TASK_STAGE, TODO_TASK_STAGE, STUDIES_DELIVERY_TASK, PROJECT_NAME_TASK, DELIVERY_INFOS_TASK, FULLFILLEMENT_TASK, IN_PROGRESS_PROJECT_STAGE
state_done = {'kanban_state': 'done'}
state_normal = {'kanban_state': 'normal'}

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
            values.update({
                'type_of_project': 'operation',
                'stage_id': self.env.ref('choreograph_project.planning_project_stage_draft').id,
            })
        return super().create(values)
