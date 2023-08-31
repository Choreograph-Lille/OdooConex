# -*- coding: utf-8 -*-

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        if view_type == "form" and (
                self.user_has_groups("choreograph_sox.group_validator_1_purchase_profile_res_groups") or
                self.user_has_groups("choreograph_sox.group_validator_2_purchase_profile_res_groups")
        ):
            view_id = self.env.ref("choreograph_purchase.purchase_order_form_validator_inherit").id
        return super(PurchaseOrder, self).get_view(view_id, view_type, **options)
