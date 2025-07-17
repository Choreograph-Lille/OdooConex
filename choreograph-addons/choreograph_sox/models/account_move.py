# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

from odoo.exceptions import ValidationError, AccessError


class AccountMove(models.Model):
    _inherit = "account.move"

    is_preparer = fields.Boolean(compute='compute_user_role')
    is_validator = fields.Boolean(compute='compute_user_role')
    is_accountant = fields.Boolean(compute='compute_user_role')

    def compute_user_role(self):
        for rec in self:
            rec.is_preparer = self.env.user.has_group("choreograph_sox.group_purchasing_preparer_profile_res_groups")
            rec.is_validator = self.env.user.has_group("choreograph_sox.group_validator_1_purchase_profile_res_groups")
            rec.is_accountant = self.env.user.has_group("choreograph_sox.group_accounting_profile_res_groups")

    def action_gap_not_justified(self):
        raise ValidationError(_('The gap must be justified before confirmation'))

    def action_gap_not_validated(self):
        raise ValidationError(_('The gap must be validated before confirmation'))
    
    @api.model_create_multi
    def create(self, vals_list):
        if (
            (
                self._context.get('default_move_type') in ['out_refund', 'in_refund'] or 
                any(vals.get('move_type') in ['out_refund', 'in_refund'] for vals in vals_list)
            )  and not self.env.user.has_group('choreograph_sox.group_credit_note_preparer_profile_res_groups')
        ):
            raise AccessError(_("You don't have access to create refund."))
        
        records = super(AccountMove, self).create(vals_list)
        return records
    
    def action_post(self):
        if self.env.user.has_group('choreograph_sox.group_credit_note_validator_profile_res_groups'):
            res = super(AccountMove, self.with_context(force_write=True)).action_post()
        else:
            res = super(AccountMove, self).action_post()
        return res
    
    def write(self, vals):
       
        if (
            self.move_type in ['out_refund', 'in_refund'] and 
            self.env.user != self.env.ref('base.user_root') and
            not self.env.user.has_group('choreograph_sox.group_credit_note_preparer_profile_res_groups') and
            not self._context.get('force_write')
        ):
            raise AccessError(_("You don't have access to edit refund."))
        
        res = super(AccountMove, self).write(vals)
        return res

