# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    retribution_cost = fields.Float(compute='_compute_retribution_cost', store=True)

    def _timesheet_service_generation(self):
        if self._context.get('is_operation_generation'):
            super(SaleOrderLine, self)._timesheet_service_generation()

    @api.depends('product_uom_qty', 'price_unit', 'order_id.related_base')
    def _compute_retribution_cost(self):
        for rec in self:
            if rec.product_id.concerned_base:
                rec.retribution_cost = rec.product_uom_qty * rec.price_unit
                if rec.product_id.concerned_base.is_multi_base:
                    rec.retribution_cost *= rec.product_id.concerned_base.retribution_rate_multi_base
                else:
                    rec.retribution_cost *= rec.product_id.concerned_base.retribution_rate
            else:
                rec.retribution_cost = 0

    @api.depends('price_subtotal', 'product_uom_qty', 'purchase_price')
    def _compute_margin(self):
        super()._compute_margin()
        for line in self:
            line.margin -= line.retribution_cost
            line.margin_percent = line.price_subtotal and line.margin / line.price_subtotal
