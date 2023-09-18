# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import models, api, _


class StudioApprovalEntry(models.Model):
    _inherit = 'studio.approval.entry'

    @api.model_create_multi
    def create(self, vals_list):
        entries = super().create(vals_list)
        for entry in entries:
            if entry.model == 'purchase.order' and entry.method == 'button_confirm' and entry.group_id.id == self.env.ref("choreograph_sox.group_validator_1_purchase_profile_res_groups").id:
                self.env[entry.model].browse(entry.res_id).update_purchase_user(entry.user_id)
        return entries
