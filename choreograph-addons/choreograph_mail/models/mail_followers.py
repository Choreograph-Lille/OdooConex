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
        tmp_vals_list = self.check_partner_group(vals_list)
        res = super(MailFollowers, self).create(tmp_vals_list)
        res._invalidate_documents(tmp_vals_list)
        return res

    def check_partner_group(self, vals):
        """
        Check if the user related to the created record's partner_id exists and is an internal user
        If not we don't create the follower
        :param vals: value from create()
        :return: vals without non-internal users
        """
        values = copy.deepcopy(vals)
        if not self.env.context.get('manual_follower_add', False):
            for value in vals:
                if value.get('partner_id'):
                    user = self.env['res.users'].search([('partner_id', '=', value['partner_id'])], limit=1)
                    if not user or not user.has_group('base.group_user'):
                        values.remove(value)
        return values
