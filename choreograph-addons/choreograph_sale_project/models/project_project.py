# -*- coding: utf-8 -*-

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta

from odoo.addons.choreograph_project.models.project_project import (
    TERMINATED_TASK_STAGE,
    TODO_TASK_STAGE,
    WAITING_FILE_TASK_STAGE,
    WAITING_QTY_TASK_STAGE,
    BAT_CLIENT_TASK_STAGE
)


class ProjectProject(models.Model):
    _inherit = 'project.project'

    project_template_id = fields.Many2one('project.project', 'Operation Template',
                                          domain=[('is_template', '=', True)], copy=False)

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

    def create_operation_from_template(self):
        action = self.project_template_id.create_project_from_template(self.name)
        self.unlink()
        return action

    def create_project_from_template(self, name=False):
        action = super(ProjectProject, self).create_project_from_template()
        project = self.browse(action.get('res_id')).exists()
        if project.type_of_project == 'operation':
            types = self.env['project.task'].get_operation_project_task_type()
            project_stage = self.env.ref('choreograph_project.planning_project_stage_draft')
            task_stage = self.env.ref('choreograph_project.project_task_type_draft')
            project.write({
                'stage_id': project_stage.id,
                'type_ids': [(6, 0, types.ids)],
                'name': name if name else project.name
            })
            project.task_ids.with_context(task_stage_init=True).write({
                'stage_id': task_stage.id,
            })
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'sale.order',
                'target': 'current',
                'context': {
                    'create_project_from_template': True,
                    'operation_id': action.get('res_id')
                }
            }
        return action

    def initialize_order(self, order_id):
        self.write({
            'sale_order_id': order_id.id,
            'partner_id': order_id.partner_id.id,
            'user_id': order_id.user_id.id
        })
        self.task_ids.write({
            'sale_order_id': order_id.id,
            'partner_id': order_id.partner_id.id,
            'date_deadline': order_id.commitment_date
        })
        self.task_ids.filtered(lambda t: t.task_number in ['80']).write({
            'date_deadline': order_id.commitment_date - relativedelta(days=2) if order_id.commitment_date else False,
        })

    def write(self, vals):
        res = super(ProjectProject, self).write(vals)
        for record in self:
            if record.type_of_project == 'operation' and \
                    vals.get('stage_id') == self.env.ref('choreograph_project.planning_project_stage_planified').id:
                record._hook_stage_planified()
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
        self._update_task_stage('40', TODO_TASK_STAGE)

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
        task_55 = self._find_task_by_task_number('55')
        task_45 = self._find_task_by_task_number('45')
        task_55_in_80 = task_55 and task_55.stage_id.stage_number == TERMINATED_TASK_STAGE
        task_45_in_80 = task_45 and task_45.stage_id.stage_number == BAT_CLIENT_TASK_STAGE
        if (task_55_in_80 or not task_55) and (task_45_in_80 or not task_45):
            self._update_task_stage('75', TODO_TASK_STAGE)

    def _hook_task_55_in_stage_80(self):
        task_70 = self._find_task_by_task_number('55')
        task_45 = self._find_task_by_task_number('45')
        task_45_in_80 = task_45 and task_45.stage_id.stage_number == BAT_CLIENT_TASK_STAGE
        task_70_in_80 = task_70 and task_70.stage_id.stage_number == TERMINATED_TASK_STAGE
        if (task_70_in_80 or not task_70) and (task_45_in_80 or not task_45):
            self._update_task_stage('75', TODO_TASK_STAGE)

    def _hook_task_75_in_stage_80(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_presta_delivery').id})

    def _hook_task_10_and_80_in_stage_80(self, task_number):
        if self._is_task_terminated(['10', '80'], task_number):
            self._update_task_stage('85', TODO_TASK_STAGE)

    def _hook_task_fulfillement_terminated(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_to_deliver').id})

    def _hook_task_45_in_stage_80(self):
        self._update_task_stage('90', TODO_TASK_STAGE)

    def _hook_task_45_in_stage_50(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_routing').id})

    def _hook_task_80_in_stage_80(self):
        self._update_task_stage('85', TODO_TASK_STAGE)

    def _hook_task_90_in_stage_15(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_extraction').id})

    def _hook_task_90_in_stage_80(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_terminated').id})

    def _hook_check_all_task(self, task_id):
        not_terminated = self.task_ids.filtered(
            lambda task: task.id != task_id and task.stage_id.stage_number != TERMINATED_TASK_STAGE)
        if not not_terminated:
            self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_terminated').id})
