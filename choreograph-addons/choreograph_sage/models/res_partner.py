# -*- coding: utf-8 -*-

from odoo import models, fields, api


PAYMENT_CHOICE = [
    ('vsep', 'VSEP'),
    ('prv', 'PRV'),
    ('virint', 'VIRINT'),
    ('cbb', 'CBB'),
    ('chq', 'CHQ'),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _default_third_party_role_client_code(self):
        return self.parent_id.third_party_role_client_code if self.parent_id else False

    def _default_third_party_role_supplier_code(self):
        return self.partner_id.third_party_role_supplier_code if self.parent_id else False

    third_party_role_client_code = fields.Char(compute='compute_parent_fields', inverse='inverse_parent_fields', store=True)
    third_party_role_supplier_code = fields.Char(compute='compute_parent_fields', inverse='inverse_parent_fields', store=True)
    customer_payment_choice = fields.Selection(PAYMENT_CHOICE, compute='compute_parent_fields', inverse='inverse_parent_fields', store=True)
    supplier_payment_choice = fields.Selection(PAYMENT_CHOICE, compute='compute_parent_fields', inverse='inverse_parent_fields', store=True)
    cartesis_code = fields.Char(compute='compute_parent_fields', inverse='inverse_parent_fields', store=True)

    @api.depends('parent_id', 'parent_id.third_party_role_client_code', 'parent_id.third_party_role_client_code', 'parent_id.third_party_role_supplier_code', 'parent_id.cartesis_code')
    def compute_parent_fields(self):
        for rec in self:
            rec.third_party_role_client_code = rec.parent_id.third_party_role_client_code if rec.parent_id else rec.third_party_role_client_code
            rec.third_party_role_supplier_code = rec.parent_id.third_party_role_supplier_code if rec.parent_id else rec.third_party_role_supplier_code
            rec.customer_payment_choice = rec.parent_id.customer_payment_choice if rec.parent_id else rec.customer_payment_choice
            rec.supplier_payment_choice = rec.parent_id.supplier_payment_choice if rec.parent_id else rec.supplier_payment_choice
            rec.cartesis_code = rec.parent_id.cartesis_code if rec.parent_id else rec.cartesis_code

    def inverse_parent_fields(self):
        self.child_ids.compute_parent_fields()
