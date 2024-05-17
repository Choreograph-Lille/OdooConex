# -*- encoding: utf-8 -*-
from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    pbi_function_app_url = fields.Char('PBI Function App URL')
    pbi_table_filter = fields.Char('PBI Table Filter')
    pbi_column_filter = fields.Char('PBI Column Filter')
    pbi_value_filter = fields.Char('PBI Value Filter')

    @api.depends('commercial_partner_id', 'commercial_partner_id.pbi_function_app_url', 'is_company', 'parent_id.commercial_partner_id')
    def _compute_operation_home_url(self):
        for rec in self:
            rec.pbi_function_app_url = rec.commercial_partner_id.pbi_function_app_url

    @api.model_create_multi
    def create(self, val_list):
        res = super(ResPartner, self).create(val_list)
        res.update_pbi_fields()
        return res

    def write(self, values):
        res = super().write(values)
        for rec in self:
            pbi_fields = ['pbi_function_app_url', 'pbi_table_filter', 'pbi_column_filter', 'pbi_value_filter']
            if rec.is_company and any([field in values for field in pbi_fields]) or 'commercial_partner_id' in values:
                self.update_pbi_fields()
        return res

    def update_pbi_fields(self):
        for rec in self:
            if rec.is_company:
                rec.child_ids._update_pbi_fields()
            else:
                rec._update_pbi_fields()

    def _update_pbi_fields(self):
        for rec in self:
            rec.write({
                'pbi_function_app_url': rec.commercial_partner_id.pbi_function_app_url,
                'pbi_table_filter': rec.commercial_partner_id.pbi_table_filter,
                'pbi_column_filter': rec.commercial_partner_id.pbi_column_filter,
                'pbi_value_filter': rec.commercial_partner_id.pbi_value_filter,
            })
