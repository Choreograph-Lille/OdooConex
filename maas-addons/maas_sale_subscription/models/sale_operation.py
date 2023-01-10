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

from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api, _


class SaleOperation(models.Model):
    _inherit = 'sale.operation'

    balance = fields.Integer('Balance', compute='compute_balance', store=True)

    @api.depends('partner_id', 'partner_id.subscription_ids', 'partner_id.subscription_ids.state', 'partner_id.subscription_ids.balance')
    def compute_balance(self):
        for rec in self:
            balance = 0
            if not rec.partner_id:
                balance = 0
            else:
                subscription = rec.partner_id.get_active_subscription()
                if subscription:
                    balance = subscription.balance
            rec.balance = balance

    def check_quantity(self):
        self.ensure_one()
        result = super(SaleOperation, self).check_quantity()
        if self.balance < 0:
            raise ValidationError(_('The balance is not enough.'))
        return result


class SaleOperatinChild(models.Model):
    _inherit = 'sale.operation.child'

    def command_ordered(self):
        self.ensure_one()
        line_obj = self.env['sale.order.line']
        subscription = self.operation_id.partner_id.get_active_subscription()
        if not subscription:
            raise UserError(_('No active subscription was found for this customer.'))
        if subscription:
            self.check_quantity(self.qty_extracted)
        if subscription.balance >= self.qty_extracted or subscription.current_package_id.unlimited:
            product = subscription.current_package_id
            quantity = subscription.current_cumulative_quantity + self.qty_extracted
            current_product_pricelist = subscription.pricelist_id or subscription.partner_id.property_product_pricelist
            if product and subscription._check_pricelist_item_exists(product):
                line_obj.create({'product_id': product.id,
                                 'name': product.name,
                                 'date': fields.Datetime.now(),
                                 'order_id': subscription.id,
                                 'product_uom_qty': 1,
                                 'product_uom': product.uom_id.id,
                                 'price_unit': current_product_pricelist._get_product_price(product, 1),
                                 'qty_consumed': self.qty_extracted, 'qty_cumulative': quantity,
                                 'state_subscription': 'consumption'})
            elif product and not subscription._check_pricelist_item_exists(product):
                line_obj.create({'product_id': product.id,
                                 'name': product.name,
                                 'date': fields.Datetime.now(),
                                 'order_id': subscription.id,
                                 'product_uom_qty': 1,
                                 'product_uom': product.uom_id.id,
                                 'price_unit': product.list_price,
                                 'qty_consumed': self.qty_extracted,
                                 'qty_cumulative': quantity,
                                 'state_subscription': 'consumption'})
            balance = subscription.balance - self.qty_extracted
            subscription.write({'current_cumulative_quantity': quantity, 'balance': balance})
            self.write({'state': 'ordered'})
            self.operation_id.qty_extracted += self.qty_extracted
            template = self.env.ref('maas_sale.operation_ordered_mail_template')
            self.send_mail(template.with_context(stage='stage_02'))
            return True
        identifiers = subscription.current_package_id.identifiers + self.qty_extracted - subscription.balance
        pricelist_products = subscription.pricelist_id.mapped('item_ids').mapped('product_tmpl_id')
        products = self.env['product.product'].search([('identifiers', '>=', identifiers),
                                                       ('recurring_invoice', '=', True),
                                                       ('product_tmpl_id', 'in', pricelist_products.ids)],
                                                      order='identifiers asc')
        if not products and subscription.current_package_id.unlimited == False:
            raise ValidationError(
                _('No upper level to propose in product pricelist. Please contact your system administrator.'))
        context = {
            'default_subscription_id': subscription.id,
            'default_operation_id': self.id,
            'default_product_id': products[0].id,
            'product_name': products[0].name,
        }
        return self.env['package.upgrade'].open_wizard(name=_('Package Upgrade Assistant'), context=context)
