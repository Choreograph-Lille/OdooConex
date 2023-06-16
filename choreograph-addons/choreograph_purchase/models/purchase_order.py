# -*- coding: utf-8 -*-

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    date_approve = fields.Datetime("Order Date")

    def action_rfq_send(self):
        result = super(PurchaseOrder, self).action_rfq_send()
        if not self.env.context.get('send_rfq', False):
            template = self.env.ref("choreograph_purchase.email_template_purchase_done", raise_if_not_found=False)
            result['context'].update({
                'default_use_template': bool(template),
                'default_template_id': template.id,
            })
        return result