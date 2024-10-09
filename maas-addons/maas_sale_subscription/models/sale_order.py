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
from odoo import fields, models, api, _
from odoo.tools import str2bool
from datetime import date
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

SUBSCRIPTION_STATES = [('to_invoice', 'To Invoice'),
                       ('invoiced', 'Invoiced'),
                       ('consumption', 'Consumption'),
                       ('start_subscription', 'Start Subscription / Article'),
                       ('subscription_change', 'Subscription change / Article'),
                       ('subscription_rent', 'Rent')]


class SaleSubscription(models.Model):
    _inherit = 'sale.order'

    allowance = fields.Selection([('crm', 'CRM'), ('prm', 'PRM')], default='crm')

    @api.model_create_multi
    def create(self, val_list):
        for vals in val_list:
            if vals.get('package_id'):
                vals['balance'] = self.env['product.product'].browse(vals.get('package_id')).identifiers
        return super(SaleSubscription, self).create(val_list)

    def _get_pricelist(self):
        self.ensure_one()
        pricelist = self.pricelist_id or self.partner_id.property_product_pricelist
        pricelist = pricelist or self.env.ref('product.list0', raise_if_not_found=False)
        return pricelist

    def _manage_subscription_start(self):
        self.ensure_one()
        if not self.start_date:
            self.start_date = fields.Date.today()
        self.create_subscription_rent()
        vals = self._prepare_start_subscription_line_values(self.current_package_id)
        self.order_line = [(0, 0, vals)]

    def action_confirm(self):
        self.ensure_one()
        result = super(SaleSubscription, self).action_confirm()
        if self.is_subscription:
            self.with_context(come_from_action_confirm=True)._manage_subscription_start()
        return result

    @api.onchange('package_id')
    def _onchange_package(self):
        self.balance = self.package_id.identifiers
        self.current_package_id = self.package_id.id

    def _prepare_line_to_invoice_values(self, line):
        self.ensure_one()
        if not line.product_id or not self.sale_order_template_id:
            return {}
        pricelist = self._get_pricelist()
        product = line.product_id
        price = self._get_price(product, pricelist, line)
        return {
            'order_id': self.id,
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'product_uom': line.product_id.uom_id.id,
            'product_uom_qty': 1,
            'price_unit': price,
            'state_subscription': 'invoiced',
            'qty_cumulative': line.qty_cumulative,
        }
    
    def _get_price(self, product, pricelist, line):
        order_template = self.sale_order_template_id
        if order_template.with_rent is False:
            if line.qty_cumulative <= order_template.minimal_consumption:
                price = order_template.minimal_price
            else:
                price = line.qty_cumulative * order_template.cost_per_thousand
        else:
            price = pricelist._get_product_price(product, 1)
        return price

    def _prepare_start_subscription_line_values(self, product):
        self.ensure_one()
        if not product:
            return {}
        pricelist = self._get_pricelist()
        price = pricelist._get_product_price(product, 1)
        return {
            'order_id': self.id,
            'product_id': product.id,
            'name': product.name,
            'product_uom_qty': 1,
            'product_uom': product.uom_id.id,
            'price_unit': price,
            'date': fields.Datetime.now(),
        }

    def _prepare_subscription_rent_line_values(self, product=False):
        return self._prepare_start_subscription_line_values(product)

    @api.model
    def _manage_recurring_invoice_lines(self):
        """
        Create line to invoice
        :return:
        """
        subscription_obj = self.env['sale.order']
        subscription_line_obj = self.env['sale.order.line']
        # Disable today domain for subscription next_inovice_date
        # subscriptions = subscription_obj.search([('is_subscription', '=', True), ('next_invoice_date', '=', fields.Date.today()),
        #                                          ('current_package_id', '!=', False), ('stage_id.category', '=', 'progress')])

        subscriptions = subscription_obj.search([('is_subscription', '=', True),
                                                 ('current_package_id', '!=', False), ('stage_id.category', '=', 'progress')])

        # Change current_datetime
        # current_datetime = fields.Datetime.now()
        # _logger.info("Subscription CRON launched at %s" % current_datetime)

        # start_period = current_datetime.replace(hour=2, minute=0, second=0) + relativedelta(day=1)
        # end_period = current_datetime.replace(hour=21, minute=59, second=59, microsecond=999) + relativedelta(day=31)

        for subscription in subscriptions:
            # Set next_invoice_date to current_date
            current_datetime = datetime.combine(subscription.next_invoice_date, datetime.min.time())
            _logger.info("Subscription CRON launched at %s" % current_datetime)

            start_period = current_datetime.replace(hour=2, minute=0, second=0) + relativedelta(day=1)
            end_period = current_datetime.replace(hour=21, minute=59, second=59, microsecond=999) + relativedelta(day=31)
            
            # Disable date filter for order_line
            # lines = subscription.order_line.filtered(
            #     lambda l: l.state_subscription == 'consumption' and start_period <= l.date <= end_period
            # )
            lines = subscription.order_line.filtered(
                lambda l: l.state_subscription == 'consumption'
            )
            lines_invoiced = subscription.order_line.filtered(
                lambda l: l.state_subscription == 'invoiced'
            )
            if lines and not lines_invoiced:
                line = lines[-1:]
                vals = subscription._prepare_line_to_invoice_values(line)
                vals.update({'date': end_period})
                _logger.info(_('To invoice line added in subscription %s') % subscription.name)
                new_line = subscription_line_obj.new(vals)
                new_line._compute_amount()
                subscription_line_obj.create(new_line._convert_to_write(new_line._cache))
                self.env.cr.commit()
            product = subscription.package_id
            vals = subscription._prepare_start_subscription_line_values(product)
            date_start_rent = end_period + relativedelta(months=1, day=1)
            vals.update({'date': date_start_rent})
            _logger.info(_('Start subscription line added in subscription %s') % subscription.name)

            subscription.write({'balance': subscription.package_id.identifiers,
                                'current_cumulative_quantity': 0,
                                'current_package_id': subscription.package_id.id})
            
            if subscription.sale_order_template_id and subscription.sale_order_template_id.with_rent:
                subscription.create_subscription_rent(date_start_rent)
                new_line = subscription_line_obj.new(vals)
                new_line._compute_amount()
                subscription_line_obj.create(new_line._convert_to_write(new_line._cache))
        return subscriptions

    def get_subscription_rent_items(self):
        self.ensure_one()
        items = self.pricelist_id.mapped('item_ids') or self.partner_id.property_product_pricelist.mapped('item_ids')
        items_rent = items.filtered(lambda j: j.subscription_rent)
        return items_rent

    def create_subscription_rent(self, date_start_rent=False):
        self.ensure_one()
        items = self.get_subscription_rent_items()
        pricelist = self._get_pricelist()
        for item in items:
            product = item.product_tmpl_id.product_variant_id
            vals = self._prepare_subscription_rent_line_values(product)
            vals.update({
                'state_subscription': 'subscription_rent',
                'temporal_type': 'subscription',
                'price_unit': pricelist._get_product_price(product, 1)
            })
            if not self._context.get('come_from_action_confirm'):
                vals.update({
                    'date': date_start_rent
                })
            self.order_line = [(0, 0, vals)]
        return True

    @api.onchange('partner_id')
    def _onchange_partner_id_warning(self):
        result = super(SaleSubscription, self)._onchange_partner_id_warning()
        pricelist = self._get_pricelist()
        products = self.env['product.product'].search([('recurring_invoice', '=', True),
                                                       ('is_basic_package', '=', True),
                                                       ('id', 'in', pricelist.item_ids.mapped('product_tmpl_id').ids)],
                                                      order='identifiers asc')
        if products:
            product = products[0]
            self.package_id = product
        return result
    
    def _get_invoiceable_lines_with_rent(self, start_period, end_period, subscription, invoiceable_lines):
        rent_line = subscription.order_line.filtered(
            lambda l: l.state_subscription == 'subscription_rent' and start_period <= l.date <= end_period
        )
        consumption_lines = subscription.order_line.filtered(
            lambda l: l.state_subscription == 'consumption' and start_period <= l.date <= end_period
        )
        if consumption_lines and rent_line:
            invoiceable_lines |= rent_line[0]
            invoiceable_lines |= consumption_lines[-1:]
        else:
            start_subscription_line = subscription.order_line.filtered(
                lambda l: l.state_subscription == 'start_subscription' and start_period <= l.date <= end_period
            )
            if start_subscription_line and rent_line:
                invoiceable_lines |= rent_line[0]
                invoiceable_lines |= start_subscription_line[0]
        
        return invoiceable_lines
    

    def _get_invoiceable_lines(self, final=False):
        """
        Override to implement the choreograph invoice policy
        :param final:
        :return:
        """
        invoiceable_lines = super(SaleSubscription, self)._get_invoiceable_lines(final)
        invoiceable_lines = invoiceable_lines.filtered(lambda invl: not invl.order_id.is_subscription)

        # Change today datetime
        # date = fields.Datetime.now()

        # start_period = date.replace(hour=0, minute=0, second=0) + relativedelta(day=1)
        # end_period = date.replace(hour=23, minute=59, second=59, microsecond=999) + relativedelta(day=31)

        for subscription in self.filtered(lambda sub: sub.is_subscription and sub.sale_order_template_id):
            date = datetime.combine(subscription.next_invoice_date, datetime.min.time())
            start_period = date.replace(hour=0, minute=0, second=0) + relativedelta(day=1)
            end_period = date.replace(hour=23, minute=59, second=59, microsecond=999) + relativedelta(day=31)
            if subscription.sale_order_template_id.with_rent:
                invoiceable_lines = subscription._get_invoiceable_lines_with_rent(start_period, end_period, subscription, invoiceable_lines)
            else:
                line = subscription.order_line.filtered(
                    lambda l: l.state_subscription == 'invoiced' and start_period <= l.date <= end_period
                )
                if line:
                    invoiceable_lines |= line[0]
                else:
                    continue
            
        _logger.info(_("Lines to invoice: %s") % str(invoiceable_lines.mapped("name")))
        return invoiceable_lines

    @api.model
    def _cron_recurring_create_invoice(self):
        subscriptions = self._manage_recurring_invoice_lines()
        config_obj = self.env['ir.config_parameter'].sudo()
        if not str2bool(config_obj.get_param('recurring.invoice.scheduler.enabled')):
            subscriptions._update_next_invoice_date()
            subscriptions._set_next_invoice_date_to_end_of_month()
            return False
        invoices = super(SaleSubscription, subscriptions)._cron_recurring_create_invoice()
        _logger.info(_("Invoices created: %s") % str(invoices))
        subscriptions._set_next_invoice_date_to_end_of_month()
        return invoices

    def _set_next_invoice_date_to_end_of_month(self):
        """
        force the next invoice date to the end of month
        """
        for subscription in self:
            subscription.write({'next_invoice_date':  subscription.next_invoice_date + relativedelta(months=1, day=1, days=-1)})

    def _handle_automatic_invoices(self, auto_commit, invoices):
        """
        Overwrite to bypass the validation auto of invoices
        """
        return invoices
