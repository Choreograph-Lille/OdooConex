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

    allowance = fields.Selection([('crm', 'CRM'), ('prm', 'PRM')], default='crm')

    @api.model
    def create(self, vals):
        if vals.get('package_id'):
            vals['balance'] = self.env['product.product'].browse(vals.get('package_id')).identifiers
        return super(SaleSubscription, self).create(vals)

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
        if not line.product_id:
            return {}
        pricelist = self._get_pricelist()
        product = line.product_id
        price = self._check_pricelist_item_exists(product) and pricelist._get_product_price(product, 1) or product.list_price
        return {
            'order_id': self.id,
            'product_id': line.product_id.id,
            'name': line.product_id.name,
            'product_uom': line.product_id.uom_id.id,
            'product_uom_qty': 1,
            'price_unit': price,
            'state_subscription': 'to_invoice',
            'qty_cumulative': line.qty_cumulative
        }

    def _prepare_start_subscription_line_values(self, product):
        self.ensure_one()
        if not product:
            return {}
        pricelist = self._get_pricelist()
        price = self._check_pricelist_item_exists(product) and pricelist._get_product_price(product, 1) or product.list_price
        return {
            'order_id': self.id,
            'product_id': product.id,
            'name': product.name,
            'product_uom_qty': 1,
            'product_uom': product.uom_id.id,
            'price_unit': price,
            'date': fields.Datetime.now()
        }

    def _prepare_subscription_rent_line_values(self, product=False, item=False):
        self.ensure_one()
        if not product or not item:
            return {}
        pricelist = self._get_pricelist()
        template = item.product_tmpl_id
        price = self._check_pricelist_item_exists(product) and pricelist._get_product_price(template, 1) or template.list_price
        return {
            'order_id': self.id,
            'product_id': product.id,
            'name': product.name,
            'product_uom_qty': 1,
            'product_uom': product.uom_id.id,
            'price_unit': price,
            'date': fields.Datetime.now()
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
            lines = subscription.order_line.filtered(lambda l: l.state_subscription == 'consumption').sorted(key='create_date',
                                                                                                             reverse=True)
            if lines:
                line = lines[0]
                vals = subscription._prepare_line_to_invoice_values(line)
                _logger.info(_('To invoice line added in subscription %s') % subscription.name)
                new_line = subscription_line_obj.new(vals)
                new_line._compute_amount()
                subscription_line_obj.create(new_line._convert_to_write(new_line._cache))
                self.env.cr.commit()
            else:
                # TODO: invoice basic package
                pass
            product = subscription.package_id
            vals = subscription._prepare_start_subscription_line_values(product)
            vals.update({'date': date_now + relativedelta(months=1, day=1)})
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
        items = self.get_subscription_rent_items()
        pricelist = self._get_pricelist()
        product = self.current_package_id
        for item in items:
            vals = self._prepare_start_subscription_line_values(product)
            vals.update({
                'state_subscription': 'subscription_rent',
                'price_unit': pricelist._get_product_price(item.product_tmpl_id, 1)
            })
            if not self._context.get('come_from_action_confirm'):
                vals.update({
                    'date': fields.Datetime.now() + relativedelta(months=1, day=1)
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

    def _check_pricelist_item_exists(self, product):
        self.ensure_one()
        return product.product_tmpl_id in self.pricelist_id.item_ids.mapped('product_tmpl_id') or False

    def _get_invoiceable_lines(self, final=False):
        invoiceable_lines = super(SaleSubscription, self)._get_invoiceable_lines(final)
        if self.is_subscription:
            return invoiceable_lines.filtered(lambda l: l.state_subscription == 'to_invoice')
        return invoiceable_lines

    @api.model
    def _cron_recurring_create_invoice(self):
        self._manage_recurring_invoice_lines()
        moves = super(SaleSubscription, self)._cron_recurring_create_invoice()
        invoiceable_lines = moves.mapped('line_ids').mapped('sale_line_ids')
        invoiceable_lines.write({'state_subscription': 'invoiced'})
        return True
