# -*- coding: utf-8 -*-

from odoo import fields, models, api


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def default_user_id(self):
        return self.partner_id.purchase_user_id or False

    date_approve = fields.Datetime("Order Date")

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = self.get_default_purchase_user(vals_list)
        return super(PurchaseOrder, self).create(vals_list)

    def get_default_purchase_user(self, vals_list):
        for val in vals_list:
            val['user_id'] = self.env['res.partner'].browse(val['partner_id']).purchase_user_id.id
        return vals_list

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
