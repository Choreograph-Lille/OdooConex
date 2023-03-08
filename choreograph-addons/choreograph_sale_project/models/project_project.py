# -*- coding: utf-8 -*-

from odoo import api, models

from odoo.addons.choreograph_project.models.project_project import (
    TERMINATED_TASK_STAGE,
    TODO_TASK_STAGE,
    WAITING_FILE_TASK_STAGE,
    WAITING_QTY_TASK_STAGE,
)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    @api.model
    def set_task_project(self):
        task_details = self.env['project.task'].get_task_list()

        def get_vals(_list):
            return {'task_ids': [(0, 0, task_details[item]) for item in _list]}

        def new_extend(source_list: list(), extend_list: list()) -> list():
            tmp = source_list.copy()
            tmp.extend(extend_list)
            return tmp
        task_list = ['project_name']
        self.env.ref('choreograph_sale_project.project_project_score_presentation').write(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_study').write(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_count').write(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_yield_calculation').write(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_matchback').write(get_vals(task_list))

        task_list.extend(['potential', 'delivery_study', 'fullfilment_client', 'delivery_infos'])
        self.env.ref('choreograph_sale_project.project_project_telfixebox_enrichment').write(
            get_vals(new_extend(task_list, ['campaign_counts'])))
        self.env.ref('choreograph_sale_project.project_project_extraction').write(get_vals(task_list))

        task_list.extend(['prefulfillment'])
        self.env.ref('choreograph_sale_project.project_project_ddn_enrichment').write(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_telportable_enrichment').write(
            get_vals(new_extend(task_list, ['campaign_counts'])))
        self.env.ref('choreograph_sale_project.project_project_sms_enrichment').write(
            get_vals(new_extend(task_list, ['audit', 'campaign_sms', 'info_presta', 'delivery_presta', 'campaign_counts'])))
        self.env.ref('choreograph_sale_project.project_project_email_enrichment').write(get_vals(new_extend(
            task_list, ['audit', 'campaign', 'file_bat', 'link_opt_out', 'info_presta', 'delivery_presta', 'campaign_counts'])))

        task_list.extend(['presentation', 'deposit_date'])
        self.env.ref('choreograph_sale_project.project_project_reactivation').write(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_loyalty').write(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_activation').write(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_postal_prospecting').write(get_vals(task_list))

        task_list.extend(['campaign_counts'])
        self.env.ref('choreograph_sale_project.project_project_postal_prospecting_telfixebox').write(
            get_vals(new_extend(task_list, ['info_presta', 'delivery_presta'])))
        self.env.ref('choreograph_sale_project.project_project_telfixebox_prospecting').write(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_postal_prospecting_email').write(
            get_vals(new_extend(task_list, ['campaign', 'file_bat', 'info_presta', 'delivery_presta'])))
        self.env.ref('choreograph_sale_project.project_project_email_prospecting').write(
            get_vals(new_extend(task_list, ['campaign', 'file_bat'])))
        self.env.ref('choreograph_sale_project.project_project_postal_prospecting_sms').write(
            get_vals(new_extend(task_list, ['campaign_sms', 'info_presta', 'delivery_presta'])))
        self.env.ref('choreograph_sale_project.project_project_sms_prospecting').write(
            get_vals(new_extend(task_list, ['campaign_sms'])))
        self.env.ref('choreograph_sale_project.project_project_postal_prospecting_telportable').write(
            get_vals(new_extend(task_list, ['info_presta', 'delivery_presta'])))
        self.env.ref('choreograph_sale_project.project_project_prospection_telportable').write(get_vals(task_list))

    def create_project_from_template(self):
        action_id = super().create_project_from_template()
        project_id = self.browse(action_id.get('res_id')).exists()
        if project_id and project_id.type_of_project == 'operation':
            type_ids = self.env['project.task'].get_operation_project_task_type()
            project_stage_id = self.env.ref('choreograph_project.planning_project_stage_draft').id
            task_stage_id = self.env.ref('choreograph_project.project_task_type_draft').id
            project_id.write({
                'stage_id': project_stage_id,
                'type_ids': [(6, 0, type_ids.ids)]
            })
            project_id.task_ids.with_context(task_stage_init=True).write({
                'stage_id': task_stage_id,
            })
        return action_id

    def write(self, vals):
        res = super(ProjectProject, self).write(vals)
        if self.type_of_project == 'operation' and vals.get('stage_id', False) == self.env.ref('choreograph_project.planning_project_stage_planified').id:
            self._hook_stage_planified()
        return res

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

    def _hook_task_65_5_15_terminated(self, except_task):
        if self._is_task_terminated(['65', '5', '15'], except_task):
            if self.task_ids.filtered(lambda task: task.task_number == '70'):
                self._update_task_stage('70', TODO_TASK_STAGE)
            else:
                self._update_task_stage('80', TODO_TASK_STAGE)

    def _is_task_terminated(self, task_number_list, task_number=False):
        if task_number and task_number in task_number_list:
            task_number_list.pop(task_number_list.index(task_number))
        task_ids = self.task_ids.filtered(lambda task: task.task_number in task_number_list)
        return all([task.stage_id.stage_number == TERMINATED_TASK_STAGE for task in task_ids])

    def _hook_task_70_in_stage_80(self):
        self._update_task_stage('75', TODO_TASK_STAGE)

    def _hook_task_75_in_stage_80(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_presta_delivery').id})

    def _hook_task_10_and_80_in_stage_80(self, task_number):
        if self._is_task_terminated(['10', '80'], task_number):
            self._update_task_stage('85', TODO_TASK_STAGE)

    def _hook_task_fulfillement_terminated(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_delivery').id})

    def _hook_task_45_in_80_or_90_in_15(self):
        self._update_task_stage('90', TODO_TASK_STAGE)

    def _hook_task_80_in_stage_80(self):
        self._update_task_stage('85', TODO_TASK_STAGE)

    def _hook_task_90_in_stage_15(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_extraction').id})

    # HT00832: function not used
    # def _hook_task_90_in_stage_80(self):
    #     self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_terminated').id})
    #     self._update_95_to_15_with_commitment_date()

    def _hook_check_all_task(self, task_id):
        not_terminated = self.task_ids.filtered(
            lambda task: task.id != task_id and task.stage_id.stage_number != TERMINATED_TASK_STAGE)
        if not not_terminated:
            self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_terminated').id})
