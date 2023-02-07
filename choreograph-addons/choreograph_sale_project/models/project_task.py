# -*- coding: utf-8 -*-

from odoo import fields, models, api

from odoo.addons.choreograph_sale.models.operation_condition import TASK_NUMBER


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
    bat_from = fields.Char('From', related='sale_order_id.bat_from')
    bat_internal = fields.Char(related='sale_order_id.bat_internal')
    bat_client = fields.Char(related='sale_order_id.bat_client')
    bat_comment = fields.Text('BAT Comment', related='sale_order_id.bat_comment')
    excluded_provider = fields.Char()
    optout_comment = fields.Text()
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
    routing_base = fields.Char()
    specific_counting = fields.Text()
    send_with = fields.Char()
    deposit_date_1 = fields.Date()
    deposit_date_2 = fields.Date()
    deposit_date_3 = fields.Date()

    is_info_validated = fields.Boolean('Infos Validated')
    po_livedata_number = fields.Integer('PO Livedata Number')
    campaign_name = fields.Char()
    reception_date = fields.Date(related='sale_order_id.reception_date')
    reception_location = fields.Char('Where to find ?', related='sale_order_id.reception_location')
    personalization = fields.Boolean(related='sale_order_id.personalization')
    routing_date = fields.Date(related='sale_order_id.routing_date')
    routing_end_date = fields.Date(related='sale_order_id.routing_end_date')
    campaign_type = fields.Char()
    volume_detail = fields.Text()
    sender = fields.Char(related='sale_order_id.sender')
    quantity_to_deliver = fields.Integer()
    to_validate = fields.Integer()
    object = fields.Char()
    ab_test = fields.Boolean('A/B Test')
    is_preheader_available = fields.Boolean('Preheader available in HTML')
    comment = fields.Text(related='sale_order_id.comment')
    bat_desired_date = fields.Date()
    folder_key = fields.Char()

    segment_ids = fields.Many2many('operation.segment', compute='compute_segment_ids')
    operation_condition_ids = fields.Many2many('operation.condition', compute='compute_operation_condition_ids')

    trap_address_ids = fields.One2many('trap.address', 'task_id')
    project_task_campaign_ids = fields.One2many('project.task.campaign', 'task_id')

    @api.depends('sale_order_id', 'sale_order_id.segment_ids', 'sale_order_id.repatriate_information')
    def compute_segment_ids(self):
        if self.sale_order_id.repatriate_information:
            self.segment_ids = [(6, 0, self.env['operation.segment'].search([('order_id', '=', self.sale_order_id.id)]).ids)]
        else:
            self.segment_ids = False

    @api.depends('sale_order_id', 'sale_order_id.operation_condition_ids')
    def compute_operation_condition_ids(self):
        self.operation_condition_ids = [(6, 0, self.env['operation.condition'].search([('order_id', '=', self.sale_order_id.id)]).ids)]
