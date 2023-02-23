from odoo import models
from odoo.addons.choreograph_project.models.project_project import WAITING_FILE_TASK_STAGE, TODO_TASK_STAGE, WAITING_QTY_TASK_STAGE


class ProjectProject(models.Model):
    _inherit = 'project.project'

    def write(self, vals):
        res = super(ProjectProject, self).write(vals)
        if self.type_of_project == 'operation' and vals.get('stage_id', False) == self.env.ref('choreograph_project.planning_project_stage_planified').id:
            self._hook_stage_planified()
        return res

    def _update_task_stage(self, task_number: str, stage_number: str):
        task_id = self.task_ids.filtered(lambda task: task.task_number == task_number)
        if task_id:
            task_id.update_task_stage(stage_number)

    def _hook_stage_planified(self):
        self._update_task_stage('5', WAITING_FILE_TASK_STAGE)
        self._update_task_stage('10', WAITING_FILE_TASK_STAGE)
        self._update_task_stage('15', WAITING_FILE_TASK_STAGE)
        self._update_task_stage('20', TODO_TASK_STAGE)
        self._update_task_stage('25', TODO_TASK_STAGE)
        self._update_task_stage('35', TODO_TASK_STAGE)

    def _hook_task_in_stage_20_25(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_in_progress').id})

    def _hook_task_20_in_stage_80(self):
        self._update_task_stage('65', TODO_TASK_STAGE)

    def _hook_task_25_in_stage_80(self):
        self._update_task_stage('30', WAITING_QTY_TASK_STAGE)

    def _hook_task_30_in_stage_80(self):
        self._update_task_stage('65', TODO_TASK_STAGE)

    def _hook_all_task_terminated(self, except_task):
        if not self.task_ids.filtered(lambda task: task.task_number != '80' and task.id != except_task):
            self._update_task_stage('70', TODO_TASK_STAGE)
            self._update_task_stage('80', TODO_TASK_STAGE)

    def _hook_task_70_in_stage_80(self):
        self._update_task_stage('75', TODO_TASK_STAGE)

    def _hook_task_75_in_stage_80(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_presta_delivery').id})

    def _hook_task_10_80_in_80(self):
        self._update_task_stage('85', TODO_TASK_STAGE)

    def _hook_task_fulfillement_terminated(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_delivery').id})

    def _hook_task_90_in_stage_80(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_terminated').id})
        self._update_task_stage('95', TODO_TASK_STAGE)
