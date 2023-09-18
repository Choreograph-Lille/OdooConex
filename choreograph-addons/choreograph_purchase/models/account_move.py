# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    is_gap = fields.Boolean(compute="_compute_is_gap", store=True)
    is_gap_validated = fields.Boolean("Is Gap Validated", tracking=True)
    is_gap_justified = fields.Boolean("Is Gap Justified", tracking=True)

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
        if self.is_gap and not self.is_gap_justified:
            raise ValidationError(_("The gap must be justified before its validation!"))
        self.is_gap_validated = True
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super(AccountMove, self).create(vals_list)
        records.filtered(lambda inv: inv.move_type == "in_invoice" and inv.invoice_origin).manage_invoice_followers()
        return records

    def manage_invoice_followers(self):
        po_obj = self.env["purchase.order"]
        for record in self:
            pos = po_obj.search([("name", "in", record.invoice_origin.split(","))])
            if pos:
                record.message_subscribe(partner_ids=pos.mapped("message_follower_ids").mapped("partner_id").ids)
        return True

    def button_justify_gap(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id("choreograph_purchase.account_move_wizard_act_window")
        action["context"] = {"default_move_id": self.id}
        return action
