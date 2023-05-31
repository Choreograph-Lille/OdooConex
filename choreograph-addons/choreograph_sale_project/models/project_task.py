# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

from odoo.addons.choreograph_project.models.project_project import (
    TERMINATED_TASK_STAGE,
    FILE_RECEIVED_TASK_STAGE,
    WAITING_FILE_TASK_STAGE,
    TODO_TASK_STAGE
)
from odoo.addons.choreograph_sale.models.sale_order import REQUIRED_TASK_NUMBER


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

    bat_from = fields.Many2one('choreograph.campaign.de')
    bat_from_for_40 = fields.Char(string='From', default='IDSEQ | TOP_CANAL_SOURCE(0/1) | TOP_CANAL_ENRICHISSABLE(0/1/2) |')
    bat_internal = fields.Char()
    bat_client = fields.Char()
    bat_comment = fields.Text('BAT Comment')
    excluded_provider = fields.Char(related='sale_order_id.excluded_provider')
    optout_link = fields.Text("Output Links", related='sale_order_id.optout_link')
    witness_file_name = fields.Char('File Name')
    witness_comment = fields.Text()
    file_name = fields.Char()
    file_quantity = fields.Char()
    volume = fields.Integer()
    dedup_title_number = fields.Char()
    family_conex = fields.Boolean()

    provider_file_name = fields.Char()
    provider_delivery_address = fields.Char('Delivery Address')

    provider_comment = fields.Text()
    desired_finished_volume = fields.Char()
    start_date = fields.Date()
    routing_base = fields.Char(related='sale_order_id.routing_base')
    specific_counting = fields.Text()
    send_with = fields.Selection(related='sale_order_id.send_with')
    deposit_date_1 = fields.Date()
    deposit_date_2 = fields.Date()
    deposit_date_3 = fields.Date()

    is_info_validated = fields.Boolean('Infos Validated', related='sale_order_id.is_info_validated')
    po_livedata_number = fields.Char('PO Livedata Number')
    campaign_name = fields.Char("Campaign Name")
    reception_date = fields.Date(related='sale_order_id.email_reception_date', string="Reception Date")
    reception_location = fields.Char('Where to find ?', related='sale_order_id.email_reception_location')
    personalization = fields.Boolean(related='sale_order_id.email_personalization')
    personalization_text = fields.Text('If yes specify', related='sale_order_id.email_personalization_text')
    routing_date = fields.Date(related='sale_order_id.email_routing_date')
    routing_end_date = fields.Date(related='sale_order_id.email_routing_end_date')
    campaign_type = fields.Selection(related='sale_order_id.campaign_type')
    volume_detail = fields.Text(related='sale_order_id.email_volume_detail')
    sender = fields.Char(related='sale_order_id.email_sender')
    quantity_to_deliver = fields.Integer(related='sale_order_id.quantity_to_deliver')
    to_validate = fields.Boolean(related='sale_order_id.to_validate')
    object = fields.Char(related='sale_order_id.object')
    ab_test = fields.Boolean('A/B Test', related='sale_order_id.ab_test')
    ab_test_text = fields.Text('If so, on what?', related='sale_order_id.ab_test_text')
    is_preheader_available = fields.Boolean('Preheader available in HTML', related='sale_order_id.is_preheader_available')
    is_preheader_available_text = fields.Text('If not, indicate where to find it', related='sale_order_id.is_preheader_available_text')
    comment = fields.Text(compute='compute_comment')
    bat_desired_date = fields.Date(related='sale_order_id.bat_desired_date')
    folder_key = fields.Char(compute='_compute_folder_key', store=True)

    segment_ids = fields.Many2many('operation.segment')
    task_segment_ids = fields.One2many('operation.segment', 'task_id')
    operation_condition_ids = fields.Many2many('operation.condition', compute='compute_operation_condition_ids')

    trap_address_ids = fields.One2many('trap.address', 'task_id')
    project_task_campaign_ids = fields.Many2many('project.task.campaign', compute='compute_project_task_campaign_ids',
                                                 inverse='_inverse_project_task_campaign_ids')
    operation_provider_delivery_ids = fields.One2many('operation.provider.delivery', 'task_id', 'Provider Delivery')
    customer_commitment_date = fields.Datetime(related='sale_order_id.commitment_date', string="Customer Delivery Date")
    complexity = fields.Selection([
        ('1', '1'),
        ('2', '2'),
        ('3', '3')])
    delivery_date = fields.Date()
    stage_number = fields.Selection(related='stage_id.stage_number')
    has_enrichment_email_op = fields.Boolean(related='project_id.sale_order_id.has_enrichment_email_op', store=True)
    repatriate_information = fields.Boolean(related='sale_order_id.repatriate_information')

    @api.depends('sale_order_id.comment')
    def compute_comment(self):
        for rec in self:
            rec.comment = rec.sale_order_id.comment if rec.task_number in ['20', '25', '30'] else False

    @api.depends('project_id', 'sale_order_id.name', 'partner_id.ref', 'related_base.code')
    def _compute_folder_key(self):
        for task in self:
            combinaison_value = [
                task.project_id.code_sequence,
                task.project_id.code,
                task.related_base.code,
                task.partner_id.ref,
                task.sale_order_id.name if task.sale_order_id else False
            ]
            task.folder_key = '_'.join([str(item) for item in combinaison_value if item])

    def repatriate_quantity_information(self):
        self.segment_ids = [
            (6, 0, self.env['operation.segment'].search([('order_id', '=', self.sale_order_id.id)]).ids)]

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
            if task.type_of_project == 'operation' and vals.get('stage_id', False) and not self.env.context.get('task_stage_init', False):
                stage_id = self.env['project.task.type'].browse(vals['stage_id'])
                method_dict = {
                    '20': '_hook_task_20_in_stage_80',
                    '25': '_hook_task_25_in_stage_80',
                    '30': '_hook_task_30_in_stage_80',
                    '40': '_hook_task_40_in_stage_80',
                    '45': '_hook_task_45_in_stage_80',
                    '55': '_hook_task_55_in_stage_80',
                    '70': '_hook_task_70_in_stage_80',
                    '75': '_hook_task_75_in_stage_80',
                    '80': '_hook_task_80_in_stage_80',
                    '85': '_hook_task_fulfillement_terminated',
                    '90': '_hook_task_90_in_stage_80'
                }
                if stage_id.stage_number == TERMINATED_TASK_STAGE:
                    method_name = method_dict.get(task.task_number, None)
                    self.project_id._hook_check_all_task(task.id)
                    if task.task_number in ['65', '5', '15']:
                        task.project_id._hook_task_65_5_15_terminated(task.task_number)
                    elif method_name:
                        getattr(task.project_id, method_name)()
                    if task.task_number in ['10', '80']:
                        task.project_id._hook_task_10_and_80_in_stage_80(task.task_number)
                    if task.task_number == '60' and task.project_id.sale_order_id.has_enrichment_email_op:
                        task.project_id._update_task_stage('55', TODO_TASK_STAGE)
                elif (task.task_number in ['5', '10', '15'] and stage_id.stage_number == FILE_RECEIVED_TASK_STAGE) or (task.task_number in ['20', '25', '35'] and stage_id.stage_number == WAITING_FILE_TASK_STAGE):
                    task.project_id._hook_task_in_stage_20_25()
                elif task.task_number == '45' and stage_id.stage_number == '50':
                    task.project_id._hook_task_45_in_stage_50()
                elif task.task_number == '90' and stage_id.stage_number == '15':
                    task.project_id._hook_task_90_in_stage_15()
            provider_fields = ['provider_file_name', 'provider_delivery_address', 'family_conex', 'trap_address_ids', 'provider_comment']
            if any(field in vals for field in provider_fields) and task.task_number in ['70', '80']:
                task.update_provider_data()
        return res

    def update_provider_data(self):
        for rec in self:
            targeted_task = False
            data = {
                    'provider_file_name': rec.provider_file_name,
                    'provider_delivery_address': rec.provider_delivery_address,
                }
            if rec.task_number == '70':
                targeted_task = rec.project_id.task_ids.filtered(lambda t: t.task_number == '75')
            elif rec.task_number == '80':
                targeted_task = rec.project_id.task_ids.filtered(lambda t: t.task_number == '85')
                new_traps = self.env['trap.address'].create([{
                        'name': trap.name,
                        'segment_number': trap.segment_number,
                        'bc_number': trap.bc_number,
                    } for trap in rec.trap_address_ids])
                data.update({
                    'family_conex': rec.family_conex,
                    'provider_comment': rec.provider_comment,
                    'trap_address_ids': [(6, 0, new_traps.ids)]
                })
            if targeted_task:
                targeted_task.write(data)

    def _schedule_move_task_95_to_15_stage(self, limit=1):
        """
        Move task 95 to 15 stage
        :param limit:
        :return:
        """
        project_task_obj = self.env['project.task']
        draft_stage = self.env.ref('choreograph_project.project_task_type_draft', raise_if_not_found=False)
        if not draft_stage:
            return False
        to_do_stage = self.env.ref('choreograph_project.project_task_type_to_do', raise_if_not_found=False)
        if not to_do_stage:
            return False
        date = fields.Datetime.today() - relativedelta(days=15)
        tasks = project_task_obj.search([('stage_id', '=', draft_stage.id),
                                         ('task_number', '=', '95'),
                                         ('sale_order_id.commitment_date', '!=', False),
                                         ('sale_order_id.commitment_date', '<=', date)])
        return tasks.write({'stage_id': to_do_stage.id})

    @api.onchange('segment_ids')
    def onchange_segment_sequence(self):
        for rec in self:
            for i, l in enumerate(rec.segment_ids):
                l.segment_number = i + 1

    @api.onchange('task_segment_ids')
    def onchange_task_segment_sequence(self):
        for rec in self:
            for i, l in enumerate(rec.task_segment_ids):
                l.segment_number = i + 1
