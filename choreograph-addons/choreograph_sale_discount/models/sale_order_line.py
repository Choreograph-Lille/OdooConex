# -*- coding: utf-8 -*-
import re
from odoo import fields, models, api, _
from odoo.tools.misc import formatLang


class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	discount_source_line_id = fields.Many2one(
		'sale.order.line',

	)
	discount_line_ids = fields.One2many(
		'sale.order.line',
		'discount_source_line_id',
		compute='_compute_discount_line',
		readonly=False,
		store=True,
		precompute=True,
		ondelete='cascade',
		help='Discount notes related to this product lines'
	)
	discount_pricelist_id = fields.Many2one('product.pricelist', help="Used only to manage the discount line section name")

	@api.depends('product_id', 'price_unit', 'discount', 'product_uom_qty', 'order_id.pricelist_id')
	def _compute_discount_line(self):
		for line in self.filtered(lambda l: not l.display_type):
			order = line.order_id
			if order.recurrence_id:
				continue
			if order.show_update_pricelist:
				continue
			pricelist_rule = line.pricelist_item_id
			if pricelist_rule:
				order_date = order.date_order or fields.Date.today()
				product = line.product_id.with_context(**line._get_product_price_context())
				qty = line.product_uom_qty or 1.0
				uom = line.product_uom
				percentage_discount = [self.get_discount(pricelist_rule)]
				current_list_price = product.list_price * qty
				pricelist_item = pricelist_rule
				if pricelist_item.pricelist_id.discount_policy == 'without_discount':
					while pricelist_item.base == 'pricelist' and pricelist_item.base_pricelist_id.discount_policy == 'without_discount':
						rule_id = pricelist_item.base_pricelist_id._get_product_rule(product, qty, uom=uom, date=order_date)
						pricelist_item = self.env['product.pricelist.item'].browse(rule_id)
						percentage_discount.append(self.get_discount(pricelist_item))
				discount_value = []
				for percentage in filter(lambda item: item, percentage_discount):
					discount = current_list_price * percentage / 100
					format_discount = formatLang(self.env, order.currency_id.round(discount), currency_obj=order.currency_id)
					discount_value.append((str(percentage), format_discount))
					current_list_price -= discount
				display_discount = "\n".join([_('Discount XXX %s %s') % (
					f'{int(float(p))}%', d) for p, d in discount_value])
				if not line.discount_line_ids and line.product_id:
					line.discount_line_ids = [
						(
							0, 0,
							{
								'order_id': order.id,
								'display_type': 'line_note',
								'name': display_discount,
								'sequence': line.sequence,
								'discount_source_line_id': line.id,
								'discount_pricelist_id': order.pricelist_id.id,
							}
						)
					]
				else:
					if order.pricelist_id != line.discount_line_ids[0].discount_pricelist_id:
						new_discount_names = display_discount
					else:
						new_discount_names = self.update_discount_name(order, line.discount_line_ids[0].name, discount_value)
					line.discount_line_ids = [
						(
							1, line.discount_line_ids[0].id,
							{
								'order_id': order.id,
								'display_type': 'line_note',
								'name': new_discount_names,
								'sequence': line.sequence,
								'discount_source_line_id': line.id,
								'discount_pricelist_id': order.pricelist_id.id,
							}
						)
					]
			else:
				discount_line = line.discount_line_ids and line.discount_line_ids[0]
				if discount_line:
					order.order_line = [(2, discount_line.id)]

	def update_discount_name(self, order, name, discount_values):
		pattern = r'\b\d+(\,\d+)?%\s\d+\,\d+\b\s'
		discount_names = name.split('\n')
		new_discount_names = []
		for index, name in enumerate(discount_names):
			p, d = discount_values[index]
			d = d.replace(order.currency_id.symbol, '')
			new_discount_names.append(re.sub(pattern, f'{int(float(p))}%' + ' ' + str(d), name))
		return '\n'.join(new_discount_names)

	@staticmethod
	def get_discount(p):
		return p.price_discount if p.compute_price == 'formula' else p.percent_price
