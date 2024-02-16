# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    purchase_user_id = fields.Many2one('res.users', string='Purchase user', compute='_compute_purchase_user_id',
                                       precompute=True,  # avoid queries post-create
                                       readonly=False, store=True)

    @api.depends('parent_id')
    def _compute_purchase_user_id(self):
        for partner in self.filtered(
                lambda partner: not partner.purchase_user_id and partner.company_type == 'person' and partner.parent_id.purchase_user_id):
            partner.purchase_user_id = partner.parent_id.purchase_user_id

