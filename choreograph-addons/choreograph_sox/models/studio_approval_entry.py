# -*- coding: utf-8 -*-

from odoo import models, api


class StudioApprovalEntry(models.Model):
    _inherit = "studio.approval.entry"

    @api.model_create_multi
    def create(self, vals_list):
        entries = super(StudioApprovalEntry, self).create(vals_list)
        for record in entries.filtered(lambda entry: entry.model == "purchase.order" and entry.method == "button_confirm"):
            if record.group_id == self.env.ref("choreograph_sox.group_validator_1_purchase_profile_res_groups", raise_if_not_found=False):
                self.env["purchase.order"].browse(record.res_id)._set_validator_as_purchase_user(record.user_id)
        return entries
