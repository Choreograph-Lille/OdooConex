# -*- coding: utf-8 -*-

import logging
from pytz import timezone, utc
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, MissingError, RedirectWarning

_logger = logging.getLogger(__name__)

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

REQUIRED_TASK_NUMBER = {
    'potential_return': '25',
    'study_delivery': '30',
    'presentation': '35',
}

CUSTOM_STATE_SEQUENCE_MAP = {
    'forecast': 0,
    'lead': 1,
    'prospecting': 2,
    'qualif': 3,
    'draft': 4,
    'sent': 5,
    'sale': 6,
    'done': 7,
    'closed_won': 8,
    'adjustment': 9,
    'cancel': 10
}


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

    po_number = fields.Char('PO Number', tracking=True)
    campaign_name = fields.Char('Campaign Name', tracking=True)
    is_info_validated = fields.Boolean('Infos Validated', copy=False, tracking=True)
    routing_date = fields.Date(tracking=True)
    routing_end_date = fields.Date(tracking=True)
    desired_finished_volume = fields.Char(tracking=True)
    volume_detail = fields.Text(tracking=True)
    sender = fields.Char(tracking=True)

    reception_date = fields.Date("Reception Date", tracking=True)
    reception_location = fields.Char('Where to find ?', tracking=True)
    sms_personalization = fields.Boolean('Personalization', tracking=True)
    sms_personalization_text = fields.Text('If yes specify', tracking=True)
    sms_comment = fields.Text('Comment', tracking=True)

    bat_from = fields.Many2one('choreograph.campaign.de', tracking=True)
    bat_internal = fields.Char(tracking=True)
    bat_comment = fields.Text('BAT Comment', tracking=True)
    email_bat_comment = fields.Text('Comment', tracking=True)

    witness_file_name = fields.Char('File Name', tracking=True)
    witness_comment = fields.Text(tracking=True)
    email_witness_comment = fields.Text(string="Comment", tracking=True)

    sox = fields.Boolean('SOX', copy=False)

    # email campaign
    livedata_po_number = fields.Char('Email PO Livedata Number', tracking=True)
    email_campaign_name = fields.Char('Email Campaign Name', tracking=True)
    email_is_info_validated = fields.Boolean('Email Infos Validated', copy=False, tracking=True)
    email_reception_date = fields.Date('Email Reception Date', tracking=True)
    email_reception_location = fields.Char('Email Where to find ?', tracking=True)
    email_personalization = fields.Boolean('Email Personalization', tracking=True)
    email_personalization_text = fields.Text('If yes specify', tracking=True)
    email_routing_date = fields.Date('Email Routing Date', tracking=True)
    email_routing_end_date = fields.Date('Email Routing End Date', tracking=True)
    campaign_type = fields.Selection(
        [('instant', 'Instant Mail'), ('classic', 'Classic'), ('instant_classic', 'IM and Classic')],
        'Email Campaign Type', tracking=True)
    email_desired_finished_volume = fields.Char('Email Desired Finished Volume', tracking=True)
    email_volume_detail = fields.Text('Email Volume Detail', tracking=True)
    email_sender = fields.Char('Email Sender', tracking=True)
    object = fields.Char('Email Object', tracking=True)
    ab_test = fields.Boolean('Email A/B Test', tracking=True)
    ab_test_text = fields.Text('If so, on what?', tracking=True)
    is_preheader_available = fields.Boolean('Email Preheader Available In HTML', tracking=True)
    is_preheader_available_text = fields.Text('If not, indicate where to find it', tracking=True)
    email_comment = fields.Text('Email Comment', tracking=True)

    email_bat_from = fields.Many2one('choreograph.campaign.de', 'Email BAT From', tracking=True)
    email_bat_internal = fields.Char('Email BAT Internal', tracking=True)
    email_bat_client = fields.Char('Email BAT Client', tracking=True)
    bat_desired_date = fields.Date('Email BAT Desired Date', tracking=True)
    email_witness_file_name = fields.Char('Email File Name', tracking=True)
    excluded_provider = fields.Char('Email Excluded Provider', tracking=True)
    optout_comment = fields.Text('Email Optout Comment', tracking=True)
    optout_link = fields.Text('Email Optout Link', tracking=True)
    routing_base = fields.Char('Email Routing Base', tracking=True)
    project_task_campaign_ids = fields.One2many('project.task.campaign', 'order_id', 'Campaigns')
    state_specific = fields.Selection([
        ('forecast', 'Forecast'),
        ('lead', 'Lead'),
        ('prospecting', 'Prospecting'),
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('closed_won', 'Closed Won'),
        ('adjustment', 'Adjustment'),
        ('cancel', 'Cancelled'),
    ], string="C9H State", default='forecast', tracking=True)
    note = fields.Html(translate=True)
    commitment_date_tracked = fields.Date("Delivery Date", compute="compute_commitment_date_tracked", tracking=True, store=True)

    @api.model
    def get_sms_campaign_field(self):
        return [
            self.env.ref('choreograph_sale.field_sale_order__po_number').id,
            self.env.ref('choreograph_sale.field_sale_order__campaign_name').id,
            self.env.ref('choreograph_sale.field_sale_order__routing_date').id,
            self.env.ref('choreograph_sale.field_sale_order__routing_end_date').id,
            self.env.ref('choreograph_sale.field_sale_order__desired_finished_volume').id,
            self.env.ref('choreograph_sale.field_sale_order__volume_detail').id,
            self.env.ref('choreograph_sale.field_sale_order__sender').id,
            self.env.ref('choreograph_sale.field_sale_order__reception_date').id,
            self.env.ref('choreograph_sale.field_sale_order__reception_location').id,
            self.env.ref('choreograph_sale.field_sale_order__sms_personalization').id,
            self.env.ref('choreograph_sale.field_sale_order__sms_personalization_text').id,
            self.env.ref('choreograph_sale.field_sale_order__sms_comment').id,
            self.env.ref('choreograph_sale.field_sale_order__is_info_validated').id,
            self.env.ref('choreograph_sale.field_sale_order__bat_from').id,
            self.env.ref('choreograph_sale.field_sale_order__bat_internal').id,
            self.env.ref('choreograph_sale.field_sale_order__bat_comment').id,
            self.env.ref('choreograph_sale.field_sale_order__witness_file_name').id,
            self.env.ref('choreograph_sale.field_sale_order__witness_comment').id,
        ]

    @api.model
    def get_email_campaign_field(self):
        return [
            self.env.ref('choreograph_sale.field_sale_order__livedata_po_number').id,
            self.env.ref('choreograph_sale.field_sale_order__email_campaign_name').id,
            self.env.ref('choreograph_sale.field_sale_order__email_is_info_validated').id,
            self.env.ref('choreograph_sale.field_sale_order__email_reception_date').id,
            self.env.ref('choreograph_sale.field_sale_order__email_reception_location').id,
            self.env.ref('choreograph_sale.field_sale_order__email_personalization').id,
            self.env.ref('choreograph_sale.field_sale_order__email_personalization_text').id,
            self.env.ref('choreograph_sale.field_sale_order__email_routing_date').id,
            self.env.ref('choreograph_sale.field_sale_order__email_routing_end_date').id,
            self.env.ref('choreograph_sale.field_sale_order__campaign_type').id,
            self.env.ref('choreograph_sale.field_sale_order__email_desired_finished_volume').id,
            self.env.ref('choreograph_sale.field_sale_order__email_volume_detail').id,
            self.env.ref('choreograph_sale.field_sale_order__email_sender').id,
            self.env.ref('choreograph_sale.field_sale_order__object').id,
            self.env.ref('choreograph_sale.field_sale_order__ab_test').id,
            self.env.ref('choreograph_sale.field_sale_order__ab_test_text').id,
            self.env.ref('choreograph_sale.field_sale_order__is_preheader_available').id,
            self.env.ref('choreograph_sale.field_sale_order__is_preheader_available_text').id,
            self.env.ref('choreograph_sale.field_sale_order__email_comment').id,
            self.env.ref('choreograph_sale.field_sale_order__email_bat_from').id,
            self.env.ref('choreograph_sale.field_sale_order__email_bat_internal').id,
            self.env.ref('choreograph_sale.field_sale_order__bat_desired_date').id,
            self.env.ref('choreograph_sale.field_sale_order__email_witness_file_name').id,
            self.env.ref('choreograph_sale.field_sale_order__excluded_provider').id,
            self.env.ref('choreograph_sale.field_sale_order__optout_link').id,
            self.env.ref('choreograph_sale.field_sale_order__routing_base').id
        ]

    @api.model
    def get_mail_field_to_operation(self):
        result = []
        sms_campaign_field = self.get_sms_campaign_field()
        email_campaign_field = self.get_email_campaign_field()
        result.extend(sms_campaign_field)
        result.extend(email_campaign_field)
        result.append(self._get_commitment_date_fields())
        return result

    def write(self, values):
        if values.get('state', False) in ('draft', 'sent', 'sale', 'done', 'cancel'):
            values['state_specific'] = values['state']
        res = super(SaleOrder, self).write(values)
        operation_condition = self.operation_condition_ids.filtered(
            lambda c: not c.is_task_created and c.subtype not in ['comment', 'sale_order'])
        if self.project_ids and operation_condition:
            self.action_create_task_from_condition()
        return res

    def action_lead(self):
        self.write({'state_specific': 'lead'})

    def action_prospecting(self):
        self.write({'state_specific': 'prospecting'})

    def action_draft_native(self):
        self.write({'state_specific': 'draft'})
        # commit change to the database
        self.env.cr.commit()

        # show partner warning
        partner_warning = self._onchange_partner_id_warning() or dict()
        msg_warning = partner_warning.get('warning', dict())
        msg = ''
        if msg_warning:
            msg += msg_warning['message']
            raise RedirectWarning(
                msg,
                {
                    'type': 'ir.actions.client',
                    'tag': 'soft_reload'
                }, 'Continuer',
                {
                    'active_id': self.id,
                    'active_model': self._name,
                    'partner_warning': True
                }
            )

    def copy_for_next_year(self):
        no_delivery_date = self.filtered(lambda order: not order.commitment_date)
        if no_delivery_date:
            raise ValidationError(_('the record %s has no delivery date.') % (no_delivery_date))
        for order_id in self:
            next_year = order_id.commitment_date.replace(year=order_id.commitment_date.year + 1)
            order_id.copy({'commitment_date': next_year})

    @api.model
    def default_get(self, fields_list):
        res = super(SaleOrder, self).default_get(fields_list)
        if not res.get('data_conservation_id') and 'data_conservation_id' not in res:
            res.update({
                'data_conservation_id': self.env.ref('choreograph_sale.sale_data_conservation_3_months',
                                                     raise_if_not_found=False).id})
        return res

    @api.depends('order_line', 'order_line.retribution_cost', 'related_base')
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
        self.write({'show_operation_generation_button': False})

    def get_operation_condition_lines(self):
        return self.operation_condition_ids.filtered(
            lambda c: not c.is_task_created and c.subtype not in ['comment', 'sale_order'])

    def action_create_task_from_condition(self):
        for rec in self:
            for condition in rec.get_operation_condition_lines():
                vals = {
                    'name': condition.get_task_name(),
                    'partner_id': rec.partner_id.id,
                    'email_from': rec.partner_id.email,
                    'note': condition.note,
                    'sale_order_id': rec.id,
                    'role_id': self.env.ref('choreograph_contact.res_role_cp').id,
                    'user_ids': False,
                    'date_deadline': condition.operation_date,
                    'campaign_file_name': condition.file_name,
                    'task_number': condition.task_number,
                    'project_id': rec.project_ids[0].id,
                }
                condition.task_id = self.env['project.task'].sudo().create(vals)
                condition.task_id._compute_type_of_project()
                condition.task_id._compute_sale_order_id(rec)
                condition.task_id.onchange_role_id()

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

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(SaleOrder, self).read_group(domain, fields, groupby,
                                                offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        if 'state_specific' in groupby:
            return sorted(res, key=lambda g: CUSTOM_STATE_SEQUENCE_MAP.get(g.get('state_specific'), 1000))
        return res

    def button_closed_won(self):
        """
        set so in custom state closed won
        :return:
        """
        self.ensure_one()
        self.state_specific = "closed_won"
        return True

    def button_adjustment(self):
        """
        set so in adjustment custom state
        :return:
        """
        self.ensure_one()
        self.state_specific = "adjustment"
        return True

    def action_quotation_send(self):
        result = super(SaleOrder, self).action_quotation_send()
        if not self.recurrence_id:
            template = self.env.ref('choreograph_sale.mail_template_sale_confirmation', raise_if_not_found=False)
            result['context'].update({
                'default_use_template': bool(template),
                'default_template_id': template.id
            })
        return result

    def _prepare_invoice(self):
        result = super(SaleOrder, self)._prepare_invoice()
        result.update({
            "narration": self._get_invoice_narration()
        })
        return result
    
    def _get_lang_and_currency(self):  
        if self.env.ref('base.EUR') and self.currency_id == self.env.ref('base.EUR'):
            lang = 'fr_FR'
            currency_id = self.env.ref('base.EUR')
        elif self.env.ref('base.GBP') and self.currency_id == self.env.ref('base.GBP'):
            lang = 'en_GB'
            currency_id = self.env.ref('base.GBP')
        else:
            lang = self.partner_invoice_id.lang
            currency_id = False
        return lang, currency_id

    def _get_invoice_narration(self):
        self.ensure_one()
        lang, currency_id = self._get_lang_and_currency()   
        invoice_terms = self.with_context(lang=lang).env.company.invoice_terms_c9h if currency_id else ''
        return invoice_terms

    @api.depends('partner_shipping_id', 'partner_id', 'company_id', 'partner_invoice_id')
    def _compute_fiscal_position_id(self):
        super()._compute_fiscal_position_id()
        for order in self:
            if not order.partner_id:
                order.fiscal_position_id = False
                continue
            if order.partner_invoice_id:
                order.fiscal_position_id = order.partner_invoice_id.with_company(
                    order.company_id).property_account_position_id.id
            order.order_line._compute_tax_id()
            order.show_update_fpos = False

    def _notify_get_recipients_groups(self, msg_vals=None):
        """
            Inherit this native function so all the recipients could be treated as portal customer and
            granted access to the documents in the mail link without redirection to login page.
            See compose_partners context in choreograph_base
        :param msg_vals:
        :return:
        """
        groups = super()._notify_get_recipients_groups(msg_vals=msg_vals)
        customer = self._mail_get_partners()[self.id]
        portal_customer_group = list(next(group for group in groups if group[0] == 'portal_customer'))
        compose_partners = self._context.get('compose_partners', False)
        if portal_customer_group and compose_partners:
            compose_partners = compose_partners.filtered(lambda rp: not self.env['res.users'].sudo().search([('partner_id', '=', rp.id)]))
            portal_customer_group[1] = lambda pdata: pdata['id'] == customer.id or pdata['id'] in compose_partners.ids
        index = [i for i, e in enumerate(groups) if e[0] == 'portal_customer']
        if index:
            groups[index[0]] = tuple(portal_customer_group)
        return groups

    @api.depends('partner_id', 'partner_invoice_id')
    def _compute_payment_term_id(self):
        for order in self:
            order = order.with_company(order.company_id)
            order.payment_term_id = order.partner_invoice_id.property_payment_term_id

    def _message_track(self, fields_iter, initial_values_dict):
        if not fields_iter:
            return {}

        tracked_fields = self.fields_get(fields_iter)
        tracking = dict()
        for record in self:
            try:
                tracking[record.id] = record._mail_track(tracked_fields, initial_values_dict[record.id])
            except MissingError:
                continue

        # find content to log as body
        bodies = self.env.cr.precommit.data.pop(f'mail.tracking.message.{self._name}', {})
        for record in self:
            changes, tracking_value_ids = tracking.get(record.id, (None, None))
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtype = record._track_subtype(
                dict((col_name, initial_values_dict[record.id][col_name])
                     for col_name in changes)
            )
            if subtype:
                if not subtype.exists():
                    _logger.debug('subtype "%s" not found' % subtype.name)
                    continue
                record.message_post(
                    body=bodies.get(record.id) or '',
                    subtype_id=subtype.id,
                    tracking_value_ids=tracking_value_ids
                )
            elif tracking_value_ids:
                operation_tracking, order_tracking = record._split_project_field_to_track(tracking_value_ids)
                if operation_tracking:
                    operation_id = record.project_ids and record.project_ids[0]
                    operation_id.message_post(
                        body=bodies.get(record.id) or '',
                        tracking_value_ids=tracking_value_ids,
                        partner_ids=operation_id.message_follower_ids.mapped('partner_id').ids,
                    )
                if order_tracking:
                    record._message_log(
                        body=bodies.get(record.id) or '',
                        tracking_value_ids=order_tracking
                    )
        return tracking

    def _split_project_field_to_track(self, tracking_value_ids):
        self.ensure_one()
        operation_tracking = []
        order_tracking = []
        operation_field_list = self.get_mail_field_to_operation()
        operation_id = self.project_ids and self.project_ids[0]
        for tracking_value in tracking_value_ids:
            field_id = tracking_value[2]['field']
            if field_id in operation_field_list:
                if operation_id.stage_id and operation_id.stage_id.stage_number != '10':
                    if field_id in self.get_sms_campaign_field():
                        tracking_value[2]['field_desc'] += ' - SMS'
                    if field_id in self.get_email_campaign_field():
                        tracking_value[2]['field_desc'] += ' - EMAIL'
                    operation_tracking.append(tracking_value)
            else:
                order_tracking.append(tracking_value)
        return operation_tracking, order_tracking

    @api.depends("commitment_date")
    def compute_commitment_date_tracked(self):
        for record in self:
            record.commitment_date_tracked = record.commitment_date and self.get_date_tz(record.commitment_date)

    def _get_commitment_date_fields(self):
        return self.env.ref("choreograph_sale.field_sale_order__commitment_date_tracked", raise_if_not_found=False).id

    def get_date_tz(self, datetime_to_convert=False):
        """
            Convert datetime to date according to the TZ
        """
        if not datetime_to_convert:
            return False
        tz = timezone(self.env.user.tz or self.env.context.get('tz') or 'UTC')
        tz_date = utc.localize(datetime_to_convert).astimezone(tz)
        return tz_date

    def check_is_day_off(self, date_value):
        for leave in self.env['resource.calendar.leaves'].search([('country_base', 'in', [self.partner_id.country_base, False])]):
            if self.get_date_tz(leave.date_from).date() <= date_value <= self.get_date_tz(leave.date_to).date():
                return True
        return False

    def get_next_non_day_off(self, date_value):
        """
        Get the next non_off day
        :param date_value: the start date
        :return: the last non-off date
        """
        if date_value:
            while date_value.weekday() > 4 or self.check_is_day_off(date_value):
                date_value = date_value - timedelta(days=1)
        return date_value

    def copy(self, default=None):
        default = default or {}
        default['state_specific'] = 'prospecting'
        return super(SaleOrder, self).copy(default=default)

    @api.onchange('partner_id')
    def _onchange_partner_id_warning(self):
        if not self.partner_id:
            return
        if not isinstance(self.id, models.NewId) and self.state_specific != 'draft':
            return

        partner = self.partner_invoice_id if self.partner_invoice_id else self.partner_id

        # If partner has no warning, check its company
        if partner.sale_warn == 'no-message' and partner.parent_id:
            partner = partner.parent_id

        if partner.sale_warn and partner.sale_warn != 'no-message':
            # Block if partner only has warning but parent company is blocked
            if partner.sale_warn != 'block' and partner.parent_id and partner.parent_id.sale_warn == 'block':
                partner = partner.parent_id

            if partner.sale_warn == 'block':
                self.partner_id = False

            return {
                'warning': {
                    'title': _("Warning for %s", partner.name),
                    'message': partner.sale_warn_msg,
                }
            }
