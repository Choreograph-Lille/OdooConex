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

    def button_cancel(self):
        res = super(PurchaseOrder, self).button_cancel()
        for record in self:
            record.delete_existing_approvals(record._name, 'button_confirm', record.id)
        return res

    def delete_existing_approvals(self, model, method, res_id):
        self.ensure_one()
        entry_obj = self.env['studio.approval.entry'].sudo()
        entries = entry_obj.search([('model', '=', model), ('method', '=', method), ('res_id', '=', res_id)])
        entries.unlink()
        return True
