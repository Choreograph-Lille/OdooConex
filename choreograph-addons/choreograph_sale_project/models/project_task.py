# -*- coding: utf-8 -*-

from odoo import fields, models, api

from odoo.addons.choreograph_sale.models.operation_condition import TASK_NUMBER
from odoo.addons.choreograph_sale.models.sale_order import REQUIRED_TASK_NUMBER
from odoo.addons.choreograph_sale_project.models.sale_order import PROVIDER_DELIVERY_NUMBER


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_type_id = fields.Many2one('choreograph.project.task.type', string='Task type')
    task_number = fields.Selection(TASK_NUMBER)
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
    def set_task_project(self):
        task_details = {
            'update': {
                'name': 'MAj',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_conditions_exlclusion').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '5', 'type_of_project': 'operation',
                'sequence': 1
            },
            'update_push': {
                'name': 'MAJ REPOUSSOIR',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_conditions_exlclusion').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '10',
                'type_of_project': 'operation',
                'sequence': 2
            },
            'customer_file': {
                'name': 'FICHIER CLIENT',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_conditions_exlclusion').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '15',
                'type_of_project': 'operation',
                'sequence': 3
            },
            'project_name': {
                'name': 'NOM DU PROJET',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_study').id,
                'role_id': self.env.ref('choreograph_contact.res_role_ce').id,
                'task_number': '20',
                'type_of_project': 'operation',
                'sequence': 4
            },
            'potential': {
                'name': 'RETOUR DE POTENTIEL',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_study').id,
                'role_id': self.env.ref('choreograph_contact.res_role_ce').id,
                'task_number': '25',
                'type_of_project':
                'operation',
                'sequence': 5
            },
            'delivery_study': {
                'name': 'LIVRAISON ETUDES',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_study').id,
                'role_id': self.env.ref('choreograph_contact.res_role_ce').id,
                'task_number': '30',
                'type_of_project': 'operation',
                'sequence': 6
            },
            'presentation': {
                'name': 'PRESENTATION',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_study').id,
                'role_id': self.env.ref('choreograph_contact.res_role_ce').id,
                'task_number': '35',
                'type_of_project': 'operation',
                'sequence': 7
            },
            'prefulfillment': {
                'name': 'PREFULFILLMENT',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_operation').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '65',
                'type_of_project': 'operation',
                'sequence': 8
            },
            'fullfilment_client': {
                'name': 'FULFILLMENT CLIENT',
                'task_type_id': self.env.ref('choreograph_sale_project.choreograph_project_task_type_delivery').id,
                'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                'task_number': '85',
                'type_of_project': 'operation',
                'sequence': 9
            }}

        def get_vals(_list):
            return {'task_ids': [(0, 0, task_details[item]) for item in _list]}
        task_list = ['project_name']
        self.env.ref('choreograph_sale_project.project_project_score_presentation').update(get_vals(task_list))

        task_list.extend(['update', 'update_push', 'customer_file'])
        self.env.ref('choreograph_sale_project.project_project_study').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_count').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_yield_calculation').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_matchback').update(get_vals(task_list))

        task_list.extend(['potential', 'delivery_study', 'fullfilment_client'])
        self.env.ref('choreograph_sale_project.project_project_telfixebox_enrichment').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_extraction').update(get_vals(task_list))

        task_list.extend(['prefulfillment'])
        self.env.ref('choreograph_sale_project.project_project_ddn_enrichment').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_telportable_enrichment').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_sms_enrichment').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_email_enrichment').update(get_vals(task_list))

        task_list.extend(['presentation'])
        self.env.ref('choreograph_sale_project.project_project_postal_prospecting').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_postal_prospecting_telfixebox').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_telfixebox_prospecting').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_postal_prospecting_email').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_email_prospecting').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_postal_prospecting_sms').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_sms_prospecting').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_postal_telportable_prospecting').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_telmobile_prospecting').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_reactivation').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_loyalty').update(get_vals(task_list))
        self.env.ref('choreograph_sale_project.project_project_activation').update(get_vals(task_list))
