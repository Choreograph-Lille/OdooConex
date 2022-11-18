# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 ArkeUp (<http://www.arkeup.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from dateutil.relativedelta import relativedelta
import odoo
import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import uuid

logger = logging.getLogger(__name__)


class SaleOperation(models.Model):
    _name = 'sale.operation'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Sale Operation'
    _order = 'number desc'

    @api.model
    def default_get(self, fields):
        res = super(SaleOperation, self).default_get(fields)
        if not res.get('date'):
            res['date'] = odoo.fields.Datetime.now()
        if not res.get('company_id'):
            res['company_id'] = self.env.ref('base.main_company').id
        if not res.get('user_id'):
            res['user_id'] = self.env.user.id
        return res

    def _get_default_access_token(self):
        return str(uuid.uuid4())

    name = fields.Char('Name', required=True)
    number = fields.Char('Operation Number', default='', readonly=True)
    date = fields.Datetime('Date', tracking=True)
    company_id = fields.Many2one('res.company', 'Company', ondelete='cascade')
    partner_id = fields.Many2one('res.partner', 'Partner', ondelete='cascade', required=True,
                                 tracking=True)
    campaign_id = fields.Many2one('sale.campaign', 'Campaign', ondelete='restrict', required=True,
                                  tracking=True)
    action_id = fields.Many2one('sale.campaign.action', 'Action', tracking=True)
    type = fields.Selection([('prm', 'PRM'), ('crm', 'CRM')], 'Type', default='crm', required=True,
                            tracking=True)
    searched_profile_count = fields.Integer('Searched Profile Count Identifiers')
    population_scored_count = fields.Integer('Population Scored Count Identifiers')
    modelling_start_date = fields.Datetime('Modelling Start Date', readonly=True)
    modelling_end_date = fields.Datetime('Modelling End Date', readonly=True)
    modelling_progress = fields.Float('Modelling progress', readonly=True)
    qty_extracted = fields.Integer('Quantity Extracted', tracking=True)
    modeled_file_url = fields.Char('Modeled File URL')
    pbi_function_app_url = fields.Char('PBI Function App URL')
    pbi_table_filter = fields.Char('PBI Table Filter')
    pbi_column_filter = fields.Char('PBI Column Filter')
    pbi_value_filter = fields.Char('PBI Value Filter')
    population_scored_desc = fields.Text('Description', required=True, tracking=True)
    attachment_scored_id = fields.Many2one('ir.attachment', 'Population Scored Attachment', readonly=True)
    population_scored_filename = fields.Char(related='attachment_scored_id.store_fname', string='Attachment Name')
    population_scored_datafile = fields.Binary(related='attachment_scored_id.datas', string='Attachment')
    searched_profile_desc = fields.Text('Description', required=True, tracking=True)
    searched_profile_filename = fields.Char(related='attachment_profile_id.store_fname', string='Attachment Name')
    searched_profile_datafile = fields.Binary(related='attachment_profile_id.datas', string='Attachment')
    attachment_profile_id = fields.Many2one('ir.attachment', 'Searched Profile Attachment', readonly=True)

    is_studies = fields.Boolean('Studies', tracking=True)
    is_customer = fields.Boolean('Customer', readonly=True)
    state = fields.Selection(
        [('in_progress', 'In Progress'), ('modeled', 'Modeled'), ('ordered', 'Ordered'), ('available', 'Available'),
         ('downloaded', 'Downloaded'), ('cancel', 'Abandoned'), ('timeout', 'TimeOut'), ('deleted', 'Deleted')], string='State',
        default='in_progress', tracking=True)
    user_id = fields.Many2one('res.users', 'User', ondelete='restrict')
    date_availability = fields.Datetime('Date of availability', readonly=True)
    access_token = fields.Char('Security Token', copy=False, default=_get_default_access_token)
    is_cancel = fields.Boolean(default=False)

    child_ids = fields.One2many('sale.operation.child', 'operation_id', string="Children")
    number_child = fields.Integer("Children number", default=0)
    sens = fields.Selection([("best_scored", "Best scored"), ("least_scored", "Least scored")])

    deleted = fields.Boolean("Deleted", default=False)

    canal = fields.Selection([('SMS', 'SMS'), ('Print', 'Print'), ('Email', 'Email')], string='Canal')

    def button_modeling(self, link=False):
        """
        :param link:
        :return:
        """
        # TODO: complete this method to integrate the workflow
        self.ensure_one()
        self.write({'state': 'modeled', 'pbi_function_app_url': link})
        template = self.env.ref('maas_sale.operation_modeled_mail_template', raise_if_not_found=False)
        self.send_mail(template.with_context(stage='stage_02'))
        return True

    def button_download(self):
        # TODO: complete this method to integrate the workflow
        self.ensure_one()
        self.state = 'downloaded'
        # template = self.env.ref('maas_sale.operation_downloaded_mail_template', raise_if_not_found=False)
        # self.send_mail(template.with_context(stage='stage_02'))
        return True

    def button_available(self, link=False):
        """
        :param link:
        :return:
        """
        # TODO: complete this method to integrate the workflow
        self.ensure_one()
        self.write({'state': 'available', 'date_availability': fields.Datetime.now(), 'modeled_file_url': link})
        # template = self.env.ref('maas_sale.operation_available_mail_template')
        # self.send_mail(template.with_context(stage='stage_02'))
        return True

    def button_ordered(self):
        # TODO: complete this method to integrate the workflow
        self.ensure_one()
        self.write({'state': 'ordered'})
        return True

    def button_cancel(self):
        # TODO: complete this method to integrate the workflow
        self.ensure_one()
        self.state = 'cancel'
        # template = self.env.ref('maas_sale.operation_canceled_mail_template')
        # self.send_mail(template.with_context(stage='stage_02'))
        return True

    def button_delete(self):
        self.ensure_one()
        self.deleted = True
        self.state = 'deleted'
        template = self.env.ref('maas_sale.operation_deleted_mail_template')
        self.send_mail(template.with_context(stage='stage_02'))
        return True

    def run_attachments_process(self, population_data=None, population_name=False, profile_data=None,
                                profile_name=False):
        """
        :param population_data:
        :param population_name:
        :param profile_data:
        :param profile_name:
        :return:
        """
        self.ensure_one()
        attachment_vals = {
            'res_id': self.id,
            'res_model': self._name,
        }
        attachment_obj = self.env['ir.attachment']
        if population_data and isinstance(population_data, (str, bytes)):
            attachment_vals.update({
                'name': population_name,
                'db_datas': population_data,
                'store_fname': population_name
            })
            self.attachment_scored_id.unlink()
            self.attachment_scored_id = attachment_obj.create(attachment_vals).id
        if profile_data and isinstance(profile_data, (str, bytes)):
            attachment_vals.update({
                'name': profile_name,
                'db_datas': profile_data,
                'store_fname': profile_name
            })
            self.attachment_profile_id.unlink()
            self.attachment_profile_id = attachment_obj.create(attachment_vals).id
        return True

    @api.model
    def create(self, vals):
        vals['number'] = self.env['ir.sequence'].next_by_code('sale.operation')
        data01 = vals.pop('population_scored_datafile', None)
        name01 = vals.pop('population_scored_filename', False)
        data02 = vals.pop('searched_profile_datafile', None)
        name02 = vals.pop('searched_profile_filename', False)
        operation = super(SaleOperation, self).create(vals)
        template = self.env.ref('maas_sale.operation_created_mail_template', raise_if_not_found=False)
        operation.send_mail(template.with_context(stage='stage_02'))
        if data01 or data02:
            operation.run_attachments_process(data01, name01, data02, name02)
        return operation

    def write(self, vals):
        result = super(SaleOperation, self).write(vals)
        if vals.get('population_scored_datafile') or vals.get('searched_profile_datafile'):
            self.run_attachments_process(vals.pop('population_scored_datafile', None),
                                         vals.pop('population_scored_filename', False),
                                         vals.pop('searched_profile_datafile', None),
                                         vals.pop('searched_profile_filename', False))
        return result

    def name_get(self):
        result = []
        for op in self:
            result.append((op.id, '%s-%s' % (op.number, op.name)))
        return result

    @api.onchange('partner_id')
    def onchange_partner(self):
        self.campaign_id = False
        self.action_id = False

    @api.onchange('campaign_id')
    def onchange_campaign(self):
        self.action_id = False

    def button_show_report(self):
        self.ensure_one()
        raise UserError(_('This functionality is not deployed yet!'))

    def send_mail(self, template):
        """
        :param template:
        :return:
        """
        for operation in self:
            try:
                template.send_mail(operation.id, force_send=True, raise_exception=True)
            except Exception as e:
                logger.warning(repr(e))
        return True

    @api.model
    def scheduler_purge_attachments(self):
        operations = self.search([('state', '!=', 'in_progress')])
        self.env['ir.attachment'].search([('res_id', 'in', operations.ids), ('res_model', '=', self._name)]).unlink()
        return True

    def service_write_data(self, spc=0, psc=0, msd=False, med=False, mp=0.0):
        """
        :param spc:
        :param psc:
        :param msd:
        :param med:
        :param mp:
        :return:
        """
        self.write({'searched_profile_count': spc, 'population_scored_count': psc,
                    'modelling_start_date': med, 'modelling_end_date': msd, 'modelling_progress': mp})
        return True

    def get_recipients(self, mode=None):
        """
        :param mode:
        :return:
        """
        self.ensure_one()
        if not mode:
            return False
        recipients = []
        if self.partner_id.email:
            recipients.append(self.partner_id.email)
        users = self.env['res.users']
        if mode == 'operation_created':
            users = self.env.ref('maas_base.commercial_user', raise_if_not_found=False).user_ids
        elif mode in ('operation_available', 'operation_modeled'):
            users = self.env.ref('maas_base.standard_user', raise_if_not_found=False).user_ids
            users |= self.env.ref('maas_base.validator_user', raise_if_not_found=False).user_ids
            users = users.filtered(lambda usr: usr.partner_id.get_parent() == self.partner_id)
        elif mode in ('operation_recall_download_file', 'operation_canceled'):
            users = self.env.ref('maas_base.commercial_user', raise_if_not_found=False).user_ids
            clients = self.env.ref('maas_base.standard_user', raise_if_not_found=False).user_ids
            clients |= self.env.ref('maas_base.validator_user', raise_if_not_found=False).user_ids
            users |= clients.filtered(lambda usr: usr.partner_id.get_parent() == self.partner_id)
        elif mode == 'packaging_upgrade':
            users = self.env.ref('maas_base.commercial_user', raise_if_not_found=False).user_ids
            clients = self.env.ref('maas_base.standard_user', raise_if_not_found=False).user_ids
            clients = clients.filtered(lambda usr: usr.partner_id.get_parent() == self.partner_id)
            users |= clients
        elif mode == 'request_upgrade_package':
            users = self.env.ref('maas_base.validator_user', raise_if_not_found=False).user_ids
            users = users.filtered(lambda usr: usr.partner_id.get_parent() == self.partner_id)
        elif mode == 'operation_ordered':
            users = self.env.ref('maas_base.studies_user', raise_if_not_found=False).user_ids
            users |= self.env.ref('maas_base.commercial_user', raise_if_not_found=False).user_ids
            users = users.filtered(lambda usr: usr.partner_id.get_parent() == self.partner_id)
        elif mode == 'operation_deleted':
            users = self.env.ref('maas_base.commercial_user', raise_if_not_found=False).user_ids
            clients = self.env.ref('maas_base.standard_user', raise_if_not_found=False).user_ids
            clients |= self.env.ref('maas_base.validator_user', raise_if_not_found=False).user_ids
            users |= clients.filtered(lambda usr: usr.partner_id.get_parent() == self.partner_id)
        for user in users.filtered(lambda usr: usr.email):
            recipients.append(user.email)
        return ','.join(recipients)

    def request_package_upgrade(self):
        self.ensure_one()
        # template = self.env.ref('maas_sale.operation_request_upgrade_package_mail_template')
        # self.send_mail(template.with_context(stage='stage_02'))
        return True

    def get_login_url(self):
        return "%s/link" % (self.env['ir.config_parameter'].get_param('web.base.url'))

    @api.model
    def get_number_child(self, operation):
        return len(operation.child_ids)

    def has_child_deleted(self):
        self.ensure_one()
        for child in self.child_ids:
            if child.deleted:
                return True
        return False

    def check_quantity(self):
        self.ensure_one()
        ICPsudo = self.env['ir.config_parameter'].sudo()
        if self.qty_extracted <= 0:
            raise ValidationError(_('The quantity ordered must be strictly positive.'))
        elif self.qty_extracted > self.population_scored_count and ICPsudo.get_param(
                'maas_sale.operation_qty_scored',
                default=False):
            raise ValidationError(_('You cannot order quantity greater than the population scored.'))
        return True


class SaleOperationChild(models.Model):
    _name = 'sale.operation.child'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    name = fields.Char("Name")
    date = fields.Date("Date")
    partner_id = fields.Many2one('res.partner', string='Partner', related='operation_id.partner_id', store=True)
    state = fields.Selection(
        [('in_progress', 'In progress'), ('ordered', 'Ordered'), ('available', 'Available'),
         ('downloaded', 'Downloaded'), ('cancel', 'Abandoned'), ('timeout', 'TimeOut')], string='State',
        default='in_progress', tracking=True, readonly=True)
    date_availability = fields.Datetime('Date of availability', readonly=True)
    qty_extracted = fields.Integer('Quantity Extracted', tracking=True)
    downloaded = fields.Boolean("Downloaded")
    modeled_file_url = fields.Char('Modeled File URL')
    type = fields.Selection(
        [('initial_command', 'Initial Command'), ('cancel_replace', 'Full cancel and replace'), ('only_delta', 'Only Delta')],
        string='Type', default='initial_command', tracking=True)
    operation_id = fields.Many2one('sale.operation', string="Parent")

    deleted = fields.Boolean("Deleted", default=False)

    @api.model
    def create(self, vals):
        if 'operation_id' in vals:
            operation = self.env['sale.operation'].search([('id', '=', vals['operation_id'])])
            operation.number_child += 1
            vals['name'] = operation.number + '-' + str(operation.number_child).zfill(3)
            vals['date'] = odoo.fields.Datetime.now()
            if 'qty_extracted' in vals:
                self.with_context(operation_id=operation.id).check_quantity(vals['qty_extracted'])
        return super(SaleOperationChild, self).create(vals)

    def command_ordered(self):
        return True

    def check_quantity(self, child_qty_extracted=0):
        ICPsudo = self.env['ir.config_parameter'].sudo()
        if child_qty_extracted <= 0:
            raise ValidationError(_('The quantity ordered must be strictly positive.'))
        if self.env.context.get('operation_id', False):
            population_count = self.env['sale.operation'].browse(self.env.context.get('operation_id')).population_scored_count
            if child_qty_extracted > population_count and ICPsudo.get_param('maas_sale.operation_qty_scored', default=False):
                raise ValidationError(_('You cannot order quantity greater than the population scored.'))
        return True

    def command_available(self, link=False):
        self.ensure_one()
        self.write({'state': 'available', 'modeled_file_url': link, 'date_availability': fields.Datetime.now()})
        template = self.env.ref('maas_sale.operation_available_mail_template')
        self.send_mail(template.with_context(stage='stage_02'))
        return True

    def command_download(self):
        self.ensure_one()
        self.state = 'downloaded'
        template = self.env.ref('maas_sale.operation_downloaded_mail_template', raise_if_not_found=False)
        self.send_mail(template.with_context(stage='stage_02'))
        return True

    def command_cancel(self):
        # TODO: complete this method to integrate the workflow
        self.ensure_one()
        self.state = 'cancel'
        template = self.env.ref('maas_sale.operation_canceled_mail_template')
        self.send_mail(template.with_context(stage='stage_02'))
        return True

    def command_delete(self):
        # TODO: complete this method to integrate the workflow
        self.ensure_one()
        self.deleted = True
        return True

    def request_package_upgrade(self):
        self.ensure_one()
        template = self.env.ref('maas_sale.operation_request_upgrade_package_mail_template')
        self.send_mail(template.with_context(stage='stage_02'))
        return True

    @api.model
    def scheduler_recall_download_file(self):
        param_obj = self.env['ir.config_parameter']
        duration = param_obj.get_param('duration.availability.download')
        delay_notify = param_obj.get_param('delay.notification.before.term.download')
        if not duration or not delay_notify:
            return
        try:
            duration = int(duration)
            delay_notify = int(delay_notify)
        except Exception as e:
            logger.info(repr(e))
            return
        if delay_notify > duration:
            logger.info(_('Delay before deadline can\'t be greater than availability duration!'))
            return
        date_now = fields.Datetime.from_string(fields.Datetime.now())
        date_now = date_now.replace(hour=0, minute=0, second=0)
        date_end = date_now - relativedelta(days=duration) + relativedelta(days=delay_notify + 1)
        date_end = date_end.replace(hour=0, minute=0, second=0)
        operations = self.search([('state', '=', 'available'),
                                  ('date_availability', '>=', str(date_end)),
                                  ('date_availability', '<', str(date_end + relativedelta(days=1)))])
        if not operations:
            return
        template = self.env.ref('maas_sale.operation_recall_download_file_mail_template', raise_if_not_found=False)
        operations.send_mail(template.with_context(stage='stage_02'))
        return True

    @api.model
    def scheduler_download_checker(self):
        param_obj = self.env['ir.config_parameter']
        duration = param_obj.get_param('duration.availability.download')
        if not duration:
            return
        try:
            duration = int(duration)
        except Exception as e:
            logger.info(repr(e))
            return
        date = fields.Datetime.from_string(fields.Datetime.now()) - relativedelta(days=duration)
        operations = self.search([('state', '=', 'available'), ('date_availability', '<', str(date))])
        if not operations:
            return
        operations.write({'modeled_file_url': False, 'state': 'timeout'})
        return True

    def send_mail(self, template):
        """
        :param template:
        :return:
        """
        for operation in self:
            try:
                template.send_mail(operation.id, force_send=True, raise_exception=True)
            except Exception as e:
                logger.warning(repr(e))
        return True
