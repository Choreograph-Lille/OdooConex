# -*- coding: utf-8 -*-

from odoo import fields, models, api


from odoo.addons.choreograph_sale.models.sale_order import REQUIRED_TASK_NUMBER
from odoo.addons.choreograph_project.models.project_project import WAITING_FILE_TASK_STAGE, FILE_RECEIVED_TASK_STAGE, DRAFT_PROJECT_STAGE, PLANIFIED_PROJECT_STAGE, TERMINATED_TASK_STAGE, TODO_TASK_STAGE


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_type_id = fields.Many2one('choreograph.project.task.type', string='Task type')
    is_template = fields.Boolean(related='project_id.is_template')
    catalogue_ids = fields.Many2many('res.partner.catalogue', related='sale_order_id.catalogue_ids')
    related_base = fields.Many2one('retribution.base', related='sale_order_id.related_base')
    user_id = fields.Many2one('res.users', related='sale_order_id.user_id')

    id_title = fields.Char('ID Title', related='partner_id.ref')
    note = fields.Text('Information')
    campaign_file_name = fields.Char('File Name')
    type = fields.Char()  # this should take the type in cond/excl but another task

    bat_from = fields.Char('From', related='sale_order_id.bat_from')
    bat_internal = fields.Char(related='sale_order_id.bat_internal')
    bat_client = fields.Char(related='sale_order_id.bat_client')
    bat_comment = fields.Text('BAT Comment', related='sale_order_id.bat_comment')
    excluded_provider = fields.Char(related='sale_order_id.excluded_provider')
    # optout_comment = fields.Text(related='sale_order_id.optout_comment')
    optout_link = fields.Text(related='sale_order_id.optout_comment')
    witness_file_name = fields.Char('File Name', related='sale_order_id.witness_file_name')
    witness_comment = fields.Text(related='sale_order_id.witness_comment')
    file_name = fields.Char()
    file_quantity = fields.Char()
    volume = fields.Float()
    dedup_title_number = fields.Char()
    family_conex = fields.Boolean()
    provider_file_name = fields.Char()
    provider_delivery_address = fields.Char('Delivery Address')
    provider_comment = fields.Text()
    desired_finished_volume = fields.Char(related='sale_order_id.desired_finished_volume')
    start_date = fields.Date()
    routing_base = fields.Char(related='sale_order_id.routing_base')
    specific_counting = fields.Text()
    send_with = fields.Selection(related='sale_order_id.send_with')
    deposit_date_1 = fields.Date()
    deposit_date_2 = fields.Date()
    deposit_date_3 = fields.Date()

    is_info_validated = fields.Boolean('Infos Validated', related='sale_order_id.is_info_validated')
    po_livedata_number = fields.Char('PO Livedata Number', related='sale_order_id.livedata_po_number')
    campaign_name = fields.Char(related='sale_order_id.email_campaign_name')
    reception_date = fields.Date(related='sale_order_id.reception_date')
    reception_location = fields.Char('Where to find ?', related='sale_order_id.reception_location')
    personalization = fields.Boolean(related='sale_order_id.personalization')
    routing_date = fields.Date(related='sale_order_id.routing_date')
    routing_end_date = fields.Date(related='sale_order_id.routing_end_date')
    campaign_type = fields.Selection(related='sale_order_id.campaign_type')
    volume_detail = fields.Text(related='sale_order_id.email_volume_detail')
    sender = fields.Char(related='sale_order_id.sender')
    quantity_to_deliver = fields.Integer()
    to_validate = fields.Integer()
    object = fields.Char(related='sale_order_id.object')
    ab_test = fields.Boolean('A/B Test', related='sale_order_id.ab_test')
    is_preheader_available = fields.Boolean('Preheader available in HTML',
                                            related='sale_order_id.is_preheader_available')
    comment = fields.Text(related='sale_order_id.comment')
    bat_desired_date = fields.Date(related='sale_order_id.bat_desired_date')
    folder_key = fields.Char()

    segment_ids = fields.Many2many('operation.segment', compute='compute_segment_ids')
    operation_condition_ids = fields.Many2many('operation.condition', compute='compute_operation_condition_ids')

    trap_address_ids = fields.One2many('trap.address', 'task_id')
    project_task_campaign_ids = fields.Many2many('project.task.campaign', compute='compute_project_task_campaign_ids',
                                                 inverse='_inverse_project_task_campaign_ids')
    operation_provider_delivery_ids = fields.One2many(
        'operation.provider.delivery', 'task_id', 'Provider Delivery Tasks')

    @api.depends('sale_order_id', 'sale_order_id.segment_ids', 'sale_order_id.repatriate_information')
    def compute_segment_ids(self):
        if self.sale_order_id.repatriate_information:
            self.segment_ids = [
                (6, 0, self.env['operation.segment'].search([('order_id', '=', self.sale_order_id.id)]).ids)]
        else:
            self.segment_ids = False

    @api.depends('sale_order_id', 'sale_order_id.operation_condition_ids')
    def compute_operation_condition_ids(self):
        self.operation_condition_ids = [
            (6, 0, self.env['operation.condition'].search([('order_id', '=', self.sale_order_id.id)]).ids)]

    @api.depends('sale_order_id', 'sale_order_id.project_task_campaign_ids')
    def compute_project_task_campaign_ids(self):
        self.project_task_campaign_ids = [
            (6, 0, self.env['project.task.campaign'].search([('order_id', '=', self.sale_order_id.id)]).ids)]

    def _inverse_project_task_campaign_ids(self):
        pass

    def name_get(self):
        res = []
        for rec in self:
            name = rec.name
            if rec.date_deadline and rec.task_number in list(REQUIRED_TASK_NUMBER.values()):
                name += ' %s' % rec.date_deadline.strftime("%d/%m/%Y")
            res.append((rec.id, name))
        return res

    @api.model
    def get_task_list(self):
        return {
            'project_name': {
                'name': 'Nom Du Projet',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_study').id,
                'role_id': self.env.ref('choreograph_contact.res_role_ce').id,
                'task_number': '20',
                'type_of_project': 'operation',
                'sequence': 4
            },
            'potential': {
                'name': 'Retour De Potentiel',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_study').id,
                'role_id': self.env.ref('choreograph_contact.res_role_ce').id,
                'task_number': '25',
                'type_of_project':
                'operation',
                'sequence': 5
            },
            'delivery_study': {
                'name': 'Livraison Etudes',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_study').id,
                'role_id': self.env.ref('choreograph_contact.res_role_ce').id,
                'task_number': '30',
                'type_of_project': 'operation',
                'sequence': 6
            },
            'presentation': {
                'name': 'Presentation',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_study').id,
                'role_id': self.env.ref('choreograph_contact.res_role_ce').id,
                'task_number': '35',
                'type_of_project': 'operation',
                'sequence': 7
            },
            'audit': {
                'name': 'Audit',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_audit').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '40',
                'type_of_project': 'operation',
                'sequence': 8
            },
            'campaign': {
                'name': 'Campagne @',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_campaign').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cc').id,
                'task_number': '45',
                'type_of_project': 'operation',
                'sequence': 9
            },
            'campaign_sms': {
                'name': 'Campagne Sms',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_sms_campaign').id,
                'role_id': self.env.ref('choreograph_contact.res_role_commercial').id,
                'task_number': '50',
                'type_of_project': 'operation',
                'sequence': 10
            },
            'file_bat': {
                'name': 'Fichier BAT / Témoin',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_bat_witness_file').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '55',
                'type_of_project': 'operation',
                'sequence': 11
            },
            'link_opt_out': {
                'name': 'Lien OPT-OUT',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_link_opt_out').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '60',
                'type_of_project': 'operation',
                'sequence': 12
            },
            'prefulfillment': {
                'name': 'Prefulfillment',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_operation').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '65',
                'type_of_project': 'operation',
                'sequence': 13
            },
            'info_presta': {
                'name': 'Info presta',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_info_presta').id,
                'role_id': self.env.ref('choreograph_contact.res_role_adv').id,
                'task_number': '70',
                'type_of_project': 'operation',
                'sequence': 14
            },
            'delivery_presta': {
                'name': 'Livraison presta',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_delivery_presta').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '75',
                'type_of_project': 'operation',
                'sequence': 15
            },
            'delivery_infos': {
                'name': 'Infos livraison',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_delivery_infos').id,
                'role_id': self.env.ref('choreograph_contact.res_role_adv').id,
                'task_number': '80',
                'type_of_project': 'operation',
                'sequence': 16
            },
            'fullfilment_client': {
                'name': 'Fullfilment client',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_delivery').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '85',
                'type_of_project': 'operation',
                'sequence': 17
            },
            'campaign_counts': {
                'name': 'Comptages campagne',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_campaign_counts').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '90',
                'type_of_project': 'operation',
                'sequence': 18
            },
            'deposit_date': {
                'name': 'Date de dépôt',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_deposit_date').id,
                'role_id': self.env.ref('choreograph_contact.res_role_adv').id,
                'task_number': '95',
                'type_of_project': 'operation',
                'sequence': 19
            }
        }

    def write(self, vals):
        res = super(ProjectTask, self).write(vals)
        for task in self:
            if task.type_of_project == 'operation' and vals.get('stage_id', False):
                stage_id = self.env['project.task.type'].browse(vals['stage_id'])
                method_dict = {
                    '20': '_hook_task_20_in_stage_80',
                    '25': '_hook_task_25_in_stage_80',
                    '30': '_hook_task_30_in_stage_80',
                    '45': '_hook_task_45_in_80_or_90_in_15',
                    '70': '_hook_task_70_in_stage_80',
                    '75': '_hook_task_75_in_stage_80',
                    '90': '_hook_task_90_in_stage_80'
                }
                method_name = method_dict.get(task.task_number, None)
                if stage_id.stage_number == TERMINATED_TASK_STAGE:
                    task.project_id._hook_all_task_terminated(except_task=self.id)
                    if method_name:
                        getattr(task.project_id, method_name)()
                    if task.task_number in ['10', '80']:
                        task.project_id._hook_task_10_and_80_in_stage_80(task.task_number)
                elif task.project_id.stage_id.stage_number in [DRAFT_PROJECT_STAGE, PLANIFIED_PROJECT_STAGE] and stage_id.stage_number in [WAITING_FILE_TASK_STAGE, FILE_RECEIVED_TASK_STAGE]:
                    task.project_id._hook_task_in_stage_20_25()
                elif task.task_number == '90' and stage_id.stage_number == TODO_TASK_STAGE and not task.project_id.task_ids(lambda t: t.task_number == '45'):
                    task.project_id._hook_task_45_in_80_or_90_in_15()
        return res
