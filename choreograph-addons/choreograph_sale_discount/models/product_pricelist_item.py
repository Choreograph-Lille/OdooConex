# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ProductPricelistItem(models.Model):
	_inherit = 'product.pricelist.item'

	display_discount = fields.Char('Display discount', translate=True)
