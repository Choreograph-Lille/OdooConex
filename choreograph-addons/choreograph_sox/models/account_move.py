# -*- coding: utf-8 -*-

from odoo import api, models, fields, _

from odoo.exceptions import ValidationError, AccessError
from odoo.osv import expression


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
    
    def write(self, vals):
        if self.move_type in ['out_refund', 'in_refund'] and not self._context.get('force_write'):
            if  (
                    vals.get('state') == 'posted' and
                    self.env.user.has_group('choreograph_sox.group_credit_note_validator_profile_res_groups')
            ):
                return super(AccountMove, self.with_context(force_write=True)).write(vals)
            if(
                not self.env.user.has_group('choreograph_sox.group_credit_note_preparer_profile_res_groups')
            ):
                raise AccessError(_("You don't have access to edit refund."))
        
        res = super(AccountMove, self).write(vals)
        return res

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if (
            any(isinstance(e, list) and e[0] == 'move_type' for e in args) and
            (
                any(isinstance(e, list) and e[2] == 'in_invoice' for e in args) or
                (
                    any(isinstance(e, list) and e[1] == 'in' for e in args) and
                    any(isinstance(e, list) and isinstance(e[2], list) and 'in_invoice' in e[2] for e in args)
                )
            )
        ):
            if (
                not self.env.user.has_group("choreograph_sox.group_purchasing_preparer_profile_res_groups") and
                not self.env.user.has_group("choreograph_sox.group_validator_1_purchase_profile_res_groups") and
                not self.env.user.has_group("choreograph_sox.group_validator_2_purchase_profile_res_groups")
            ):
                args = expression.AND([[('is_confidential', '=', False)], args])
        
        return super(AccountMove, self).search(args, offset=offset, limit=limit, order=order, count=count)

