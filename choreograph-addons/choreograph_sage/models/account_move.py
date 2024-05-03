# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.choreograph_sage.models.res_partner import PAYMENT_CHOICE


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_choice = fields.Selection(PAYMENT_CHOICE, string='Payment Choice')
    wording = fields.Char(compute='_compute_wording')

    @api.depends('name', 'partner_id', 'partner_id.name')
    def _compute_wording(self):
        for rec in self:
            rec.wording = "%s / %s" % (rec.partner_id.name, rec.name)

    @api.model_create_multi
    def create(self, values):
        res = super(AccountMove, self).create(values)
        for move in res:
            if move.partner_id:
                move.update_payment_choice_from_partner()
        return res

    def update_payment_choice_from_partner(self):
        self.payment_choice = self.partner_id.payment_choice
