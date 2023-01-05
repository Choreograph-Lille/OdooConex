# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    retribution_cost = fields.Float(compute='_compute_retribution_cost')

    def _timesheet_service_generation(self):
        if self._context.get('is_operation_generation'):
            super(SaleOrderLine, self)._timesheet_service_generation()

    @api.depends('product_uom_qty', 'price_unit', 'order_id.related_base')
    def _compute_retribution_cost(self):
        for rec in self:
            if rec.product_id.retribution_rate:
                retribution_cost = rec.product_uom_qty * rec.price_unit * (rec.product_id.retribution_rate/100)
                datastore_restribution = retribution_cost * (rec.product_id.concerned_base.retribution_rate/100)
                rec.retribution_cost = retribution_cost if not rec.product_id.datastore else datastore_restribution
            else:
                rec.retribution_cost = 0
