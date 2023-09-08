# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    is_preparer = fields.Boolean(compute='compute_user_role')
    is_validator = fields.Boolean(compute='compute_user_role')

    def compute_user_role(self):
        for rec in self:
            rec.is_preparer = self.env.user.has_group('choreograph_sox.group_purchasing_preparer_profile_res_groups')
            rec.is_validator = self.env.user.has_group('choreograph_sox.group_validator_1_purchase_profile_res_groups')

    def action_gap_not_justified(self):
        raise ValidationError(_('The gap must be justified before confirmation'))

    def action_gap_not_validated(self):
        raise ValidationError(_('The gap must be validated before confirmation'))
