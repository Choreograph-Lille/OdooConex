# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    operation_type = fields.Many2one('project.project', string='Operation type', domain=[('is_template', '=', True)])
