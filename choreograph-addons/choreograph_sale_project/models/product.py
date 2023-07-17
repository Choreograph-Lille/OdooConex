# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _


class ProductTemplate(models.Model):
	_inherit = 'product.template'

	project_template_id = fields.Many2one(
		domain="[('is_template', '=', True), ('company_id', '=', current_company_id), ('allow_billable', '=', True), "
				"('allow_timesheets', 'in', [service_policy == 'delivered_timesheet', True])]"
	)
