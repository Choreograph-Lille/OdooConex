# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    activity_sector = fields.Many2one(related='partner_id.industry_id', store=True)
    category_name = fields.Char(related='partner_id.category_name', store=True)
    agency_id = fields.Many2one('res.partner', 'Agency')
    client_name = fields.Char(related='partner_id.name', store=True)

    def action_new_quotation(self):
        action = super(CrmLead, self).action_new_quotation()
        if self.agency_id:
            action['context'].update({
                'default_partner_invoice_id': self.agency_id.id,
                'default_payment_term_id': self.agency_id.property_payment_term_id.id
            })
        return action

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.update({
            'agency_id': self.partner_id.agency_id,
            'user_id': self.partner_id.user_id
        })
