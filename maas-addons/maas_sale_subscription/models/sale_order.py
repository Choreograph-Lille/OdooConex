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

    service_start_date = fields.Date(readonly=True)
    allowance = fields.Selection([('crm', 'CRM'), ('prm', 'PRM')], default='crm')

    @api.model
    def create(self, vals):
        if vals.get('package_id'):
            vals['balance'] = self.env['product.product'].browse(vals.get('package_id')).identifiers
        return super(SaleSubscription, self).create(vals)

    def action_confirm(self):
        self.ensure_one()
        super(SaleSubscription, self).action_confirm()
        if self.is_subscription:
            current_product_pricelist = self.pricelist_id or self.partner_id.property_product_pricelist
            if not self.service_start_date:
                self.service_start_date = fields.Date.today()
            product = self.current_package_id
            if self._check_pricelist_item_exists(product):
                self.order_line = [(0, 0, {'order_id': self.id,
                                           'product_id': product.id,
                                           'name': product.name,
                                           'date': fields.Datetime.now(),
                                           'product_uom': product.uom_id.id,
                                           'price_unit': current_product_pricelist._get_product_price(product, 1)})]
            else:
                self.order_line = [(0, 0, {'order_id': self.id,
                                           'product_id': product.id,
                                           'name': product.name,
                                           'date': fields.Datetime.now(),
                                           'product_uom': product.uom_id.id,
                                           'price_unit': product.list_price})]

            self.create_subscription_rent()
        return True

    @api.onchange('package_id')
    def _onchange_package(self):
        self.balance = self.package_id.identifiers
        self.current_package_id = self.package_id.id

    def _prepare_line_to_invoice_values(self, line):
        self.ensure_one()
        if not line:
            return {}
        return {
            'order_id': self.id,
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'product_uom': line.product_id.uom_id.id,
            'product_uom_qty': 1,
            'price_unit': line.product_id.list_price,
            'state_subscription': 'to_invoice',
            'qty_cumulative': line.qty_cumulative
        }

    def _prepare_start_subscription_line_values(self, line):
        self.ensure_one()
        if not line:
            return {}
        return {
            'order_id': self.id,
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'product_uom_qty': 1,
            'product_uom': line.product_id.uom_id.id,
            'price_unit': line.product_id.list_price
        }

    @api.model
    def _manage_recurring_invoice_lines(self):
        stage_obj = self.env['sale.order.stage']
        subscription_obj = self.env['sale.order']
        subscription_line_obj = self.env['sale.order.line']
        stages_in_progress = stage_obj.search([('category', '=', 'progress')])
        subscriptions = subscription_obj.search([('is_subscription', '=', True), ('next_invoice_date', '=', fields.Date.today()),
                                                 ('current_package_id', '!=', False), ('stage_id', 'in', stages_in_progress.ids)])
        date_now = fields.Datetime.now()
        _logger.info("Subscription CRON launched at %s" % date_now)
        for subscription in subscriptions:
            pricelist = subscription.pricelist_id or subscription.partner_id.property_product_pricelist
            pricelist = pricelist or self.env.ref('product.list0', raise_if_not_found=False)
            lines = subscription.order_line.filtered(lambda l: l.state_subscription == 'consumption').sorted(key='create_date',
                                                                                                             reverse=True)
            if lines:
                line = lines[0]
                vals = subscription._prepare_line_to_invoice_values(line)
                vals.update({'date': date_now})
                if subscription._check_pricelist_item_exists(line.product_id):
                    vals.update({'price_unit': current_product_pricelist._get_product_price(line.product_id, 1)})
                _logger.info(_('To invoice line added in subscription %s') % subscription.name)
                new_line = subscription_line_obj.new(vals)
                new_line._compute_amount()
                subscription_line_obj.create(new_line._convert_to_write(new_line._cache))
                self.env.cr.commit()
            product = subscription.package_id
            vals = subscription._prepare_start_subscription_line_values(line)
            vals.update({'date': date_now + relativedelta(months=1, day=1)})
            if subscription._check_pricelist_item_exists(product):
                vals.update({'price_unit': current_product_pricelist._get_product_price(product, 1)})
            _logger.info(_('Start subscription line added in subscription %s') % (subscription.name))
            subscription.create_subscription_rent()
            subscription.write({'balance': subscription.package_id.identifiers,
                                'current_cumulative_quantity': 0,
                                'current_package_id': subscription.package_id.id})
            new_line = subscription_line_obj.new(vals)
            new_line._compute_amount()
            subscription_line_obj.create(new_line._convert_to_write(new_line._cache))
        return True

    def get_subscription_rent_items(self):
        self.ensure_one()
        items = self.pricelist_id.mapped('item_ids') or self.partner_id.property_product_pricelist.mapped('item_ids')
        items_rent = items.filtered(lambda j: j.subscription_rent)
        return items_rent

    def create_subscription_rent(self):
        self.ensure_one()
        items_rent = self.get_subscription_rent_items()
        current_product_pricelist = self.pricelist_id or self.partner_id.property_product_pricelist
        product = self.current_package_id
        if items_rent:
            for item in items_rent:
                self.order_id = [(0, 0, {'order_id': self.id,
                                         'product_id': product.id,
                                         'name': product.name,
                                         'date': fields.Datetime.now(), 'uom_id': product.uom_id.id,
                                         'state_subscription': 'subscription_rent',
                                         'price_unit': current_product_pricelist._get_product_price
                                         (item.product_tmpl_id, 1)})]
        return True

    @api.onchange('partner_id')
    def _onchange_partner_id_warning(self):
        super(SaleSubscription, self)._onchange_partner_id_warning()
        current_product_pricelist = self.pricelist_id or self.partner_id.property_product_pricelist
        products = self.env['product.product'].search([('recurring_invoice', '=', True),
                                                       ('is_basic_package', '=', True),
                                                       ('id', 'in', current_product_pricelist.item_ids.mapped('product_tmpl_id').ids)],
                                                      order='identifiers asc')
        if products:
            product = products[0]
            self.package_id = product

    def _check_pricelist_item_exists(self, product):
        self.ensure_one()
        return product.product_tmpl_id in self.pricelist_id.item_ids.mapped('product_tmpl_id') or False

    def _get_invoiceable_lines(self, final=False):
        invoiceable_lines = super(SaleSubscription, self)._get_invoiceable_lines(final)
        return invoiceable_lines.filtered(
            lambda l: l.order_id.package_id and l.state_subscription == 'to_invoice' or not l.order_id.package_id)

    @api.model
    def _cron_recurring_create_invoice(self):
        self._manage_recurring_invoice_lines()
        moves = super(SaleSubscription, self)._cron_recurring_create_invoice()
        invoiceable_lines = moves.mapped('line_ids').mapped('sale_line_ids')
        invoiceable_lines.write({'state_subscription': 'invoiced'})
        return True