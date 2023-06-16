# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_gap = fields.Boolean(compute="_compute_is_gap", store=True)

    @api.depends("line_ids.purchase_line_id.order_id.amount_untaxed", "amount_untaxed")
    def _compute_is_gap(self):
        for move in self:
            is_gap = False
            amount_untaxed = sum(self.mapped("line_ids").mapped("purchase_line_id").mapped("order_id").mapped("amount_untaxed"))
            if amount_untaxed:
                gap =  (move.amount_untaxed - amount_untaxed) * 100 / amount_untaxed
                if abs(gap) >= 10:
                    is_gap = True
            move.is_gap = is_gap
