# -*- coding: utf-8 -*-
import copy
from odoo import api, models

MODEL_TO_UNFOLLOW = [
    'sale.order',
    'account.move',
    'project.project',
    'purchase.order',
    'project.task'
]


class MailFollowers(models.Model):
    _inherit = 'mail.followers'

    @api.model_create_multi
    def create(self, vals_list):
        tmp_vals_list = copy.deepcopy(vals_list)
        for values in vals_list:
            if values.get('res_model', False) in MODEL_TO_UNFOLLOW and values.get('res_id', False):
                source_id = self.env[values['res_model']].browse(values['res_id'])
                if source_id and 'partner_id' in source_id and source_id.partner_id and source_id.partner_id.id == values['partner_id'] and values in tmp_vals_list:
                    tmp_vals_list.remove(values)
                if values['res_model'] == 'project.task' and values['partner_id'] in source_id.user_ids.mapped('partner_id').ids and values in tmp_vals_list:
                    tmp_vals_list.remove(values)
        res = super(MailFollowers, self).create(tmp_vals_list)
        res._invalidate_documents(tmp_vals_list)
        return res

    @api.model
    def delete_mail_followers(self):
        for model in MODEL_TO_UNFOLLOW:
            record_ids = self.env['mail.followers'].search([('res_model', '=', model), ('partner_id', '>', 4)])
            for record in record_ids:
                source_ids = self.env[record.res_model].search([
                    ('id', '=', record.res_id)
                ])
                source_partner_ids = source_ids.filtered(lambda source: source.partner_id == record.partner_id.id)
                source_user_ids = source_ids.filtered(
                    lambda source: record.partner_id.id in source.user_ids.mapped('partner_id').ids) if model == 'project.task' else False
                if source_partner_ids or source_user_ids:
                    record.unlink()
