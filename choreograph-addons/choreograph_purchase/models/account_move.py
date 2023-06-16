# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    is_gap = fields.Boolean(compute="_compute_is_gap", store=True)
    is_gap_validated = fields.Boolean("Is Gap Validated", tracking=True)

    @api.depends("line_ids.purchase_line_id.order_id.amount_untaxed", "amount_untaxed", "is_gap_validated")
    def _compute_is_gap(self):
        for move in self:
            is_gap = False
            amount_untaxed = sum(self.mapped("line_ids").mapped("purchase_line_id").mapped("order_id").mapped("amount_untaxed"))
            if amount_untaxed and not move.is_gap_validated:
                gap =  (move.amount_untaxed - amount_untaxed) * 100 / amount_untaxed
                if abs(gap) >= 10:
                    is_gap = True
            move.is_gap = is_gap

    def button_validate_gap(self):
        self.ensure_one()
        self.is_gap_validated = True
        return True

