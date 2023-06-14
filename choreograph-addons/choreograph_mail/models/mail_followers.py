# -*- coding: utf-8 -*-
import copy
from odoo import api, models


class MailFollowers(models.Model):
    _inherit = 'mail.followers'

    @staticmethod
    def check_field_followers(source_id, field_name):
        model_name = {
            'partner_id': 'res.partner',
            'user_ids': 'res.users'
        }
        return source_id and field_name in source_id and source_id[field_name]._name == model_name[field_name] and source_id[field_name]

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.company.disable_followers:
            return super(MailFollowers, self).create(vals_list)
        tmp_vals_list = copy.deepcopy(vals_list)
        for values in vals_list:
            if values.get('res_id', False):
                source_id = self.env[values['res_model']].browse(values['res_id']).exists()
                if self.check_field_followers(source_id, 'partner_id') and source_id.partner_id.id == values['partner_id'] and values in tmp_vals_list:
                    tmp_vals_list.remove(values)
                if self.check_field_followers(source_id, 'user_ids') and values['partner_id'] in source_id.user_ids.mapped('partner_id').ids and values in tmp_vals_list:
                    tmp_vals_list.remove(values)
        res = super(MailFollowers, self).create(tmp_vals_list)
        res._invalidate_documents(tmp_vals_list)
        return res
