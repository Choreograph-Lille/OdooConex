# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountMoveWizard(models.TransientModel):
    _name = "account.move.wizard"
    _description = "Account Move Wizard"

    move_id = fields.Many2one("account.move", "Invoice", required=True, readonly=True)
    note = fields.Text("Note", required=True)

    def button_validate(self):
        self.ensure_one()
        self.move_id.message_post(
            body=self.note,
            partner_ids=self.move_id.message_follower_ids.mapped('partner_id').ids,
        )
        self.move_id.write({
            "is_gap_justified": True
        })
        return {"type": "ir.actions.act_window_close"}
