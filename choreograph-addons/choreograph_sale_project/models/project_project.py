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
    return_studies_date = fields.Date('Return To Studies Date', compute='compute_date_from_so', store=True)
    commitment_date = fields.Date('Commitment Date', compute='compute_date_from_so', store=True)

    @api.depends('sale_order_id')
    def compute_date_from_so(self):
        for rec in self:
            if rec.sale_line_id:
                sale_order = rec.sale_order_id
            else:
                sale_order = self.env['sale.order'].search([('project_id', '=', rec.id)], limit=1)
            rec.return_studies_date = sale_order.potential_return_date or sale_order.study_delivery_date
            rec.commitment_date = sale_order.get_date_tz(sale_order.commitment_date) if sale_order.commitment_date else False

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
            'partner_id': order_id.partner_id.id,
        })
        self.task_ids._compute_sale_order_id(order_id)

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

    def _hook_task_in_stage_25_50(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_in_progress').id})

    def _hook_task_20_in_stage_80(self):
        self._update_task_stage('65', TODO_TASK_STAGE)

    def _hook_task_25_in_stage_80(self):
        self._update_task_stage('30', WAITING_QTY_TASK_STAGE)
        self._update_task_stage('40', TODO_TASK_STAGE)

    def _hook_task_30_in_stage_80(self):
        if self._is_task_terminated(['40']):
            self._update_task_stage('65', TODO_TASK_STAGE)

    def _hook_task_40_in_stage_80(self):
        if self._is_task_terminated(['30']):
            self._update_task_stage('65', TODO_TASK_STAGE)

    def _hook_task_60_in_stage_80(self):
        self._update_task_stage('55', TODO_TASK_STAGE)

    def _hook_task_65_in_stage_80(self):
        self._update_task_stage('70', TODO_TASK_STAGE)

    def _is_task_terminated(self, task_number_list, task_number=False):
        if task_number and task_number in task_number_list:
            task_number_list.pop(task_number_list.index(task_number))
        task_ids = self.task_ids.filtered(lambda task: task.task_number in task_number_list)
        return all([task.stage_id.stage_number == TERMINATED_TASK_STAGE for task in task_ids])

    def _hook_task_70_in_stage_80(self):
        task_55 = self._find_task_by_task_number('55')
        task_45 = self._find_task_by_task_number('45')
        task_50 = self._find_task_by_task_number('50')
        task_10 = self._find_task_by_task_number('10')

        task_55_in_80 = task_55 and task_55.stage_id.stage_number == TERMINATED_TASK_STAGE
        task_45_in_70 = task_45 and task_45.stage_id.stage_number == BAT_CLIENT_TASK_STAGE
        task_50_in_70 = task_45 and task_50.stage_id.stage_number == BAT_CLIENT_TASK_STAGE
        task_10_in_80 = task_45 and task_10.stage_id.stage_number == TERMINATED_TASK_STAGE
        if (task_55_in_80 or not task_55) and ((task_45_in_70 or not task_45) or (task_50_in_70 or not task_45)) and (task_10_in_80 or not task_10):
            self._update_task_stage('75', TODO_TASK_STAGE)

    def _hook_task_55_in_stage_80(self):
        task_70 = self._find_task_by_task_number('70')
        task_45 = self._find_task_by_task_number('45')
        task_45_in_80 = task_45 and task_45.stage_id.stage_number == BAT_CLIENT_TASK_STAGE
        task_70_in_80 = task_70 and task_70.stage_id.stage_number == TERMINATED_TASK_STAGE
        if (task_70_in_80 or not task_70) and (task_45_in_80 or not task_45):
            self._update_task_stage('75', TODO_TASK_STAGE)

    def _hook_task_75_in_stage_80(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_presta_delivery').id})

    def _hook_task_fulfillement_terminated(self):
        tasks_in_80 = self.task_ids.filtered(lambda task: task.task_number not in ['35', '45,' '50', '90', '95'])
        if all([task.stage_number == TERMINATED_TASK_STAGE for task in tasks_in_80]):
            self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_to_deliver').id})

    def _hook_task_45_50_in_stage_80(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_extraction').id})
        self._update_task_stage('90', TODO_TASK_STAGE)

    def _hook_task_45_50_in_stage_50(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_routing').id})

    def _hook_task_80_in_stage_80(self):
        self._update_task_stage('85', TODO_TASK_STAGE)

    def _hook_task_90_in_stage_80(self):
        self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_livery').id})
        self._update_task_stage('95', TODO_TASK_STAGE)
        so = self.sale_order_id or self.env['sale.order'].search([('project_id', '=', self.id)])
        self._find_task_by_task_number('95').write({
            'date_deadline': so.get_date_tz(so.commitment_date) + relativedelta(days=15)
        })

    def _hook_check_all_task(self, task_id):
        not_terminated = self.task_ids.filtered(
            lambda task: task.id != task_id and task.stage_id.stage_number != TERMINATED_TASK_STAGE)
        if not not_terminated:
            self.write({'stage_id': self.env.ref('choreograph_project.planning_project_stage_terminated').id})
