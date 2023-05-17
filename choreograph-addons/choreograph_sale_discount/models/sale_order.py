# -*- coding: utf-8 -*-

from odoo import _, fields, models
from odoo.tools.misc import formatLang

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def write(self, values):
        res = super().write(values)
        if 'order_line' in values:
            self.update_discount_note()
        return res

    @staticmethod
    def get_discount(p):
        return p.price_discount if p.compute_price == 'formula' else p.percent_price

    def update_discount_note(self):
        if self.recurrence_id:
            return
        for line in self.order_line.filtered(lambda line: not line.display_type):
            pricelist_rule = line.pricelist_item_id
            if pricelist_rule:
                order_date = line.order_id.date_order or fields.Date.today()
                product = line.product_id.with_context(**line._get_product_price_context())
                qty = line.product_uom_qty or 1.0
                uom = line.product_uom
                percentage_discount = [self.get_discount(pricelist_rule)]
                current_list_price = product.list_price * qty
                pricelist_item = pricelist_rule
                if pricelist_item.pricelist_id.discount_policy == 'without_discount':
                    while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
                        rule_id = pricelist_item.base_pricelist_id._get_product_rule(
                            product, qty, uom=uom, date=order_date)
                        pricelist_item = self.env['product.pricelist.item'].browse(rule_id)
                        percentage_discount.append(self.get_discount(pricelist_item))
                discount_value = []
                for percentage in filter(lambda item: item, percentage_discount):
                    discount = current_list_price * percentage / 100
                    format_discount = formatLang(self.env, self.currency_id.round(discount), currency_obj=self.currency_id)
                    discount_value.append((str(percentage), format_discount))
                    current_list_price -= discount
                display_discount = "\n".join([_('Discount XXX %s %s') % (
                    f'{int(float(p))}%', d) for p, d in discount_value])
                source_line_id = self.env['sale.order.line'].search([('discount_source_line_id', '=', line.id)])
                if not source_line_id:
                    self.env['sale.order.line'].create({
                        'order_id': self.id,
                        'display_type': 'line_note',
                        'name': display_discount,
                        'sequence': line.sequence,
                        'discount_source_line_id': line.id
                    })
                else:
                    source_line_id.write({'name': display_discount})
            else:
                self.env['sale.order.line'].search([('discount_source_line_id', '=', line.id)]).unlink()

    def action_update_prices(self):
        self.update_discount_note()
        return super().action_update_prices()
