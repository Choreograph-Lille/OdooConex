# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    sale_order_id = fields.Many2one("sale.order", "Sale Order", compute="_compute_sale_order_id", store=True, compute_sudo=True)
    user_id = fields.Many2one('res.users', tracking=False)

    def action_invoice_sent(self):
        result = super(AccountMove, self).action_invoice_sent()
        template = self.env.ref("choreograph_account.email_template_edi_invoice", raise_if_not_found=False)
        result["context"].update({
            "default_use_template": bool(template),
            "default_template_id": template and template.id or False,
        })

        return result

    @api.depends('line_ids.sale_line_ids')
    def _compute_sale_order_id(self):
        for move in self:
            orders = move.line_ids.mapped("sale_line_ids").mapped("order_id")
            move.sale_order_id = orders and orders[0].id or False

    @api.model
    def _get_mail_partner(self):
        adresses = self.partner_id
        if self.partner_id.child_ids:
            adresses |= self.partner_id.child_ids.filtered(lambda rp: rp.type == 'invoice')
        return ','.join([str(rp.id) for rp in adresses])
