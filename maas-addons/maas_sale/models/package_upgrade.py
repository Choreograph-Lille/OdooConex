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

import logging
from odoo import models, fields, api

logger = logging.getLogger(__name__)


class PackageUpgrade(models.TransientModel):
    _name = 'package.upgrade'
    _description = 'Package Upgrade'

    product_id = fields.Many2one('product.product', 'Product', readonly=True)
    identifiers = fields.Integer(related='product_id.identifiers', readonly=True)
    operation_id = fields.Many2one('sale.operation.child', 'Operation', readonly=True)
    subscription_id = fields.Many2one('sale.order', 'Subscription', readonly=True)

    def button_validate(self):
        self.ensure_one()
        self.subscription_id.write({
            'balance': self.identifiers - self.subscription_id.current_cumulative_quantity,
            'current_package_id': self.product_id.id,
        })
        line_obj = self.env['sale.order.line']
        current_product_pricelist = self.subscription_id.pricelist_id or self.subscription_id.partner_id.property_product_pricelist
        if self.subscription_id and self.subscription_id._check_pricelist_item_exists(self.product_id):
            line_obj.create({'order_id': self.subscription_id.id,
                             'product_id': self.product_id.id,
                             'name': self.product_id.name,
                             'date': fields.Datetime.now(),
                             'product_uom_qty': 1,
                             'product_uom': self.product_id.uom_id.id,
                             'price_unit': current_product_pricelist._get_product_price(self.product_id, 1),
                             'qty_consumed': 0,
                             'qty_cumulative': self.subscription_id.current_cumulative_quantity,
                             'state_subscription': 'subscription_change'})
        else:
            line_obj.create({'order_id': self.subscription_id.id,
                             'product_id': self.product_id.id,
                             'name': self.product_id.name,
                             'date': fields.Datetime.now(),
                             'product_uom_qty': 1,
                             'product_uom': self.product_id.uom_id.id,
                             'price_unit': self.product_id.list_price,
                             'qty_consumed': 0,
                             'qty_cumulative': self.subscription_id.current_cumulative_quantity,
                             'state_subscription': 'subscription_change'})
        template = self.env.ref('maas_sale.packaging_upgrade_mail_template')
        self.operation_id.send_mail(template.with_context(stage='stage_02'))
        self.operation_id.command_ordered()

    def open_wizard(self, **kwargs):
        action = {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_id': False,
            'res_id': self.ids and self.ids[0] or False,
            'domain': [],
            'target': 'new',
        }
        action.update(**kwargs)
        return action
