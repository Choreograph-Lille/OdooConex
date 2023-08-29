# -*- coding: utf-8 -*-
import copy
from odoo import api, models


class MailFollowers(models.Model):
    _inherit = 'mail.followers'

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.company.disable_followers:
            return super(MailFollowers, self).create(vals_list)
        tmp_vals_list = self._check_is_internal_followers(vals_list)
        res = super(MailFollowers, self).create(tmp_vals_list)
        res._invalidate_documents(tmp_vals_list)
        return res

    def _check_is_internal_followers(self, vals):
        """
        Check if the user related to the created record's partner_id exists and is an internal user
        If not we don't create the follower
        :param vals: value from create()
        :return: vals without non-internal users
        """
        values = copy.deepcopy(vals)
        if not self.env.context.get('manual_follower_add', False):
            partner_obj = self.env['res.partner']
            for value in vals:
                if value.get('partner_id'):
                    users = partner_obj.browse(value['partner_id']).user_ids
                    if users and users[0].has_group('base.group_user'):
                        continue
                    values.remove(value)
        return values
