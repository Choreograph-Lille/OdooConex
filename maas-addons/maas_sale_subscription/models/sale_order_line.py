# -*- encoding: utf-8 -*-

import odoo
from odoo import fields, models, api


SUBSCRIPTION_STATES = [('to_invoice', 'To Invoice'),
                       ('invoiced', 'Invoiced'),
                       ('consumption', 'Consumption'),
                       ('start_subscription', 'Start Subscription / Article'),
                       ('subscription_change', 'Subscription change / Article'),
                       ('subscription_rent', 'Rent')]


class SaleSubscriptionLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model
    def default_get(self, fields):
        res = super(SaleSubscriptionLine, self).default_get(fields)
        if not res.get('date'):
            res['date'] = odoo.fields.Datetime.now()
        return res

    date = fields.Datetime()
    period = fields.Char(compute='compute_period', store=True)
    identifiers = fields.Integer(related='product_id.identifiers')
    qty_consumed = fields.Integer('Consumed', readonly=True)
    qty_cumulative = fields.Integer('Accrued Consumption', readonly=True)
    state_subscription = fields.Selection(SUBSCRIPTION_STATES, 'Action', default='start_subscription', readonly=True)

    @api.depends('date')
    def compute_period(self):
        for line in self:
            if line.date:
                line.period = fields.Datetime.from_string(line.date).strftime('%b-%y')

    # @api.depends('price_unit', 'product_uom_qty', 'discount', 'order_id.pricelist_id')
    # def _compute_amount(self):
    #     super(SaleSubscriptionLine, self)._compute_amount()
    #     for line in self.filtered(lambda l: l.state_subscription != 'to_invoice' and l.order_id.is_subscription):
    #         if line.order_id.package_id:
    #             line.price_subtotal = 0
    #     for line in self.filtered(lambda l: l.state_subscription == 'to_invoice' and l.order_id.is_subscription):
    #         if line.order_id.package_id:
    #             price_rent = self.filtered(lambda l: l.state_subscription == 'subscription_rent').sorted(key='date', reverse=True)
    #             if price_rent:
    #                 line.price_subtotal += price_rent[0].price_unit

    def _reset_subscription_qty_to_invoice(self):
        res = super(SaleSubscriptionLine, self)._reset_subscription_qty_to_invoice()
        for line in self.filtered(lambda l: l.order_id.package_id):
            if line.qty_cumulative:
                line.qty_to_invoice = line.qty_cumulative
            else:
                line.qty_to_invoice = line.product_uom_qty
        return res

    def _prepare_invoice_line(self, **optional_values):
        """
        override to move subscription duration in invoice line description
        :param optional_values:
        :return:
        """
        res = super(SaleSubscriptionLine, self)._prepare_invoice_line(**optional_values)
        if self.temporal_type == 'subscription' or self.order_id.subscription_management == 'upsell':
            res.update({
                'name': self._get_invoice_line_name(),
            })
        return res

    def _get_invoice_line_name(self):
        self.ensure_one()
        if self.qty_cumulative and self.state_subscription == "consumption":
            return self.name + "\n%s Ids" % self.qty_cumulative
        return self.name
