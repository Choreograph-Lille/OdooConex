# -*- encoding: utf-8 -*-

from dateutil.relativedelta import relativedelta
import odoo
import logging
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import uuid

logger = logging.getLogger(__name__)


class SaleOperationChild(models.Model):
    _name = 'sale.operation.child'
    _description = 'Sale Operation Child'
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
    downloaded = fields.Boolean()
    modeled_file_url = fields.Char('Modeled File URL')
    type = fields.Selection(
        [('initial_command', 'Initial Command'), ('cancel_replace', 'Full cancel and replace'), ('only_delta', 'Only Delta')],
        default='initial_command', tracking=True)
    operation_id = fields.Many2one('sale.operation', string="Parent")

    deleted = fields.Boolean("Deleted", default=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'operation_id' in vals:
                operation = self.env['sale.operation'].search([('id', '=', vals['operation_id'])])
                operation.number_child += 1
                vals['name'] = operation.number + '-' + str(operation.number_child).zfill(3)
                vals['date'] = odoo.fields.Datetime.now()
                if 'qty_extracted' in vals:
                    self.with_context(operation_id=operation.id).check_quantity(vals['qty_extracted'])
        return super(SaleOperationChild, self).create(vals_list)

    def command_ordered(self):
        self.ensure_one()
        return True

    def check_quantity(self, child_qty_extracted=0):
        ICPsudo = self.env['ir.config_parameter'].sudo()
        if child_qty_extracted <= 0:
            raise ValidationError(_('The quantity ordered must be strictly positive.'))
        if self.env.context.get('operation_id', False):
            population_count = self.env['sale.operation'].browse(
                self.env.context.get('operation_id')).population_scored_count
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
