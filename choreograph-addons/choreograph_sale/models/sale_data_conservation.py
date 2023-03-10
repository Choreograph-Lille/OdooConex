# -*- coding: utf-8 -*-

from odoo import fields, models, api


class SaleDataConservation(models.Model):
    _name = 'sale.data.conservation'

    name = fields.Char(translate=True)
    active = fields.Boolean('Active', default=False)

    @api.model_create_multi
    def create(self, vals_list):
        records = self
        for vals in vals_list:
            record = self.with_context(active_test=False).search([('name', '=', vals.get('name'))], limit=1)
            if record:
                records |= record
            else:
                records |= super(SaleDataConservation, self).create(vals)
        return records
