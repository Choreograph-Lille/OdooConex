# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from .operation_condition import SUBTYPE

TASK_NAME = {
    '5': _('Update'),
    '10': _('Update Repoussoir'),
    '15': _('Client File'),
    '20': _('Project Name'),
    '25': _('Potential Return'),
    '30': _('Study Delivery'),
    '35': _('Scoring Presentation'),
    '40': _('Audit'),
    '45': _('Email Campaign'),
    '50': _('SMS Campaign'),
    '55': _('BAT/Witness File'),
    '60': _('OPT-OUT Link'),
    '65': _('Prefulfillment'),
    '70': _('Presta Info'),
    '75': _('Presta Delivery'),
    '80': _('Delivery Info'),
    '85': _('Customer Fulfillment'),
    '90': _('Campaign Couting'),
    '95': _('Deposit Date'),
}

OPERATION_TYPE = {
    'condition': 'Condition',
    'exclusion': 'Exclusion',
}
REQUIRED_TASK_NUMBER = {
    'potential_return': '25',
    'study_delivery': '30',
    'presentation': '35',
}
SUBTYPES = dict(SUBTYPE)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    show_operation_generation_button = fields.Boolean(default=True, copy=False)
    operation_condition_ids = fields.One2many('operation.condition', 'order_id')
    new_condition_count = fields.Integer(compute='_compute_new_condition_count')
    catalogue_ids = fields.Many2many('res.partner.catalogue', 'sale_order_partner_catalogue_rel',
                                     'sale_order_id', 'catalogue_id', 'Catalogues')
    prefulfill_study = fields.Boolean('Pre-fulfill study')
    related_base = fields.Many2one('retribution.base')
    data_conservation_id = fields.Many2one('sale.data.conservation', 'Data Conservation', index=True,
                                           ondelete='restrict')
    other_conservation_duration = fields.Char('Other Duration')
    show_other_conservation_duration = fields.Boolean(compute='compute_show_other_conservation_duration')
    receiver = fields.Char()
    send_with = fields.Selection([('mft', 'MFT'), ('sftp', 'SFTP'), ('email', 'Email'), ('ftp', 'FTP')])
    # operation_type_id = fields.Many2one('project.project', 'Operation Type')
    total_retribution = fields.Float(compute="_compute_total_retribution", store=True)

    po_number = fields.Char('PO Number')
    campaign_name = fields.Char()
    is_info_validated = fields.Boolean('Infos Validated', copy=False)
    routing_date = fields.Date()
    routing_end_date = fields.Date()
    desired_finished_volume = fields.Char()
    volume_detail = fields.Text()
    sender = fields.Char()

    reception_date = fields.Date()
    reception_location = fields.Char('Where to find ?')
    personalization = fields.Boolean()
    comment = fields.Text()

    bat_from = fields.Many2one('choreograph.campaign.de')
    bat_internal = fields.Char()
    bat_client = fields.Char()
    bat_comment = fields.Text('BAT Comment')

    witness_file_name = fields.Char('File Name')
    witness_comment = fields.Text()

    sox = fields.Boolean('SOX')

    # email campaign
    livedata_po_number = fields.Char('Email PO Livedata Number')
    email_campaign_name = fields.Char('Email Campaign Name')
    email_is_info_validated = fields.Boolean('Email Infos Validated', copy=False)
    email_reception_date = fields.Date('Email Reception Date')
    email_reception_location = fields.Char('Email Where to find ?')
    email_personalization = fields.Boolean('Email Personalization')
    email_routing_date = fields.Date('Email Routing Date')
    email_routing_end_date = fields.Date('Email Routing End Date')
    campaign_type = fields.Selection(
        [('instant', 'Instant Mail'), ('classic', 'Classic'), ('instant_classic', 'IM and Classic')],
        'Email Campaign Type')
    email_desired_finished_volume = fields.Char('Email Desired Finished Volume')
    email_volume_detail = fields.Text('Email Volume Detail')
    email_sender = fields.Char('Email Sender')
    object = fields.Char('Email Object')
    ab_test = fields.Boolean('Email A/B Test')
    is_preheader_available = fields.Boolean('Email Preheader Available In HTML')
    email_comment = fields.Text('Email Comment')

    email_bat_from = fields.Many2one('choreograph.campaign.de', 'Email BAT From')
    email_bat_internal = fields.Char('Email BAT Internal')
    email_bat_client = fields.Char('Email BAT Client')
    bat_desired_date = fields.Date('Email BAT Desired Date')
    email_witness_file_name = fields.Char('Email File Name')
    excluded_provider = fields.Char('Email Excluded Provider')
    optout_comment = fields.Text('Email Optout Comment')
    optout_link = fields.Text('Email Optout Link')
    routing_base = fields.Char('Email Routing Base')
    project_task_campaign_ids = fields.One2many('project.task.campaign', 'order_id', 'Email Campaign')
    state_specific = fields.Selection([
        ('forecast', 'Forecast'),
        ('lead', 'Lead'),
        ('prospecting', 'Prospecting'),
        ('qualif', 'Qualif'),
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], default='forecast', string='State')

    def write(self, values):
        if values.get('state', False) in ('draft', 'sent', 'sale', 'done', 'cancel'):
            values['state_specific'] = values['state']
        return super().write(values)

    def action_lead(self):
        self.write({'state_specific': 'lead'})

    def action_prospecting(self):
        self.write({'state_specific': 'prospecting'})

    def action_qualif(self):
        self.write({'state_specific': 'qualif'})

    def action_draft_native(self):
        self.write({'state_specific': 'draft'})

    @ api.model
    def default_get(self, fields_list):
        res = super(SaleOrder, self).default_get(fields_list)
        if not res.get('data_conservation_id') and 'data_conservation_id' not in res:
            res.update({
                'data_conservation_id': self.env.ref('choreograph_sale.sale_data_conservation_3_months',
                                                     raise_if_not_found=False).id})
        return res

    @ api.depends('order_line')
    def _compute_total_retribution(self):
        for rec in self:
            rec.total_retribution = sum(rec.order_line.mapped('retribution_cost'))

    def get_operation_product(self):
        return self.order_line.filtered(lambda l: l.operation_template_id)

    def check_for_required_tasks(self, template):
        tasks = template.task_ids.mapped('task_number')
        if any([task not in tasks for task in REQUIRED_TASK_NUMBER.values()]):
            raise ValidationError(
                _('The operation template must have the following task number: {0}, {1}, {2}').format(
                    _(TASK_NAME[REQUIRED_TASK_NUMBER['potential_return']]), _(
                        TASK_NAME[REQUIRED_TASK_NUMBER['study_delivery']]),
                    _(TASK_NAME[REQUIRED_TASK_NUMBER['presentation']])))

    def action_generate_operation(self):
        # check for tasks in operation template
        line_with_project = self.get_operation_product()
        # if line_with_project:
        #     self.check_for_required_tasks(line_with_project[0].operation_template_id)
        if not line_with_project:
            no_template = _('There is no operation to generate for the items selected in the quote')
            raise ValidationError(no_template)
        self.order_line.sudo().with_company(self.company_id).with_context(
            is_operation_generation=True, user_id=self.user_id.id)._timesheet_service_generation()
        self.project_ids.write({'type_of_project': 'operation'})

        if self.commitment_date:
            self.tasks_ids.write({
                'date_deadline': self.commitment_date.date()
            })
        self.write({'show_operation_generation_button': False})

    def action_create_task_from_condition(self):
        for rec in self:
            for condition in self.operation_condition_ids.filtered(
                    lambda c: not c.is_task_created and c.subtype not in ['comment', 'sale_order']):
                vals = {
                    'name': rec.name + '/' + OPERATION_TYPE[condition.operation_type] + '/' + _(SUBTYPES[
                        condition.subtype]),
                    'partner_id': rec.partner_id.id,
                    'email_from': rec.partner_id.email,
                    'note': condition.note,
                    'sale_order_id': rec.id,
                    'user_ids': False,
                    'date_deadline': condition.operation_date,
                    'campaign_file_name': condition.file_name,
                    'task_number': condition.task_number,
                }
                condition.task_id = self.env['project.task'].sudo().create(vals)
                rec.project_ids.task_ids = [(4, condition.task_id.id)]
                condition.is_task_created = True

    def _compute_new_condition_count(self):
        self.new_condition_count = len(self.operation_condition_ids.filtered(
            lambda c: not c.is_task_created and c.subtype not in ['comment', 'sale_order']))

    def action_view_purchase_orders(self):
        action = super().action_view_purchase_orders()
        action.update({
            'context': {'default_origin': self.name}
        })
        return action

    def _get_purchase_orders(self):
        purchases = super(SaleOrder, self)._get_purchase_orders(
        ) | self.env['purchase.order'].search([('origin', '=', self.name)])
        return purchases

    @api.depends('data_conservation_id')
    def compute_show_other_conservation_duration(self):
        self.show_other_conservation_duration = self.data_conservation_id.id == self.env.ref(
            'choreograph_sale.sale_data_conservation_other').id
