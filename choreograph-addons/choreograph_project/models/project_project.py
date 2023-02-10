from odoo import models

state_done = {'kanban_state': 'done'}
state_normal = {'kanban_state': 'normal'}
WAITING_TASK_STAGE = '10'
STUDIES_DELIVERY_TASK = '30'
PROJECT_NAME_TASK = '20'
DELIVERY_INFOS_TASK = '80'
FULLFILLEMENT_TASK = '85'
IN_PROGRESS_PROJECT_STAGE = '30'
DELIVERY_TASK_NUMBER = 30


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def js_redelivery_studies(self):
        studies_delivery_task_id = self.task_ids.filtered(lambda t: t.task_number == STUDIES_DELIVERY_TASK)
        project_name_task_id = self.task_ids.filtered(lambda t: t.task_number == PROJECT_NAME_TASK)
        main_task_id = studies_delivery_task_id or project_name_task_id
        if main_task_id:
            stage_id = self.type_ids.filtered(lambda t: t.stage_number == WAITING_TASK_STAGE)
            if stage_id:
                stage_id = stage_id[0]
                state_done.update({'stage_id': stage_id.id})
                state_normal.update({'stage_id': stage_id.id})
            main_task_id.write(state_done)
            self.task_ids.filtered(lambda t: int(t.task_number) > DELIVERY_TASK_NUMBER).write(state_normal)
        self.update_stage(IN_PROGRESS_PROJECT_STAGE)

    def js_redelivery_prod(self):
        delivery_info_task_id = self.task_ids.filtered(lambda t: t.task_number == DELIVERY_INFOS_TASK)
        fullfillement_task_id = self.task_ids.filtered(lambda t: t.task_number == FULLFILLEMENT_TASK)
        if delivery_info_task_id:
            delivery_info_task_id.write(state_done)
        if fullfillement_task_id:
            fullfillement_task_id.write(state_normal)
        self.update_stage(IN_PROGRESS_PROJECT_STAGE)

    def update_stage(self, number):
        project_stage_id = self.env['project.project.stage'].search([('stage_number', '=', number)], limit=1)
        if project_stage_id:
            self.write({'stage_id': project_stage_id.id})
