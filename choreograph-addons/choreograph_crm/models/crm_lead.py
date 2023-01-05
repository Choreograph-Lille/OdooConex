# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sox = fields.Boolean('SOX')
    activity_sector = fields.Many2one(related='partner_id.industry_id', store=True)
    category_name = fields.Char(related='partner_id.category_name', store=True)
    agency_id = fields.Many2one('res.partner', 'Agency')
    client_name = fields.Char(related='partner_id.name', store=True)

    def action_new_quotation(self):
        action = self.env.ref('sale_crm.sale_action_quotations_new', raise_if_not_found=False).read()[0]
        action['context'] = self._prepare_opportunity_quotation_context()
        action['context'].update({'search_default_opportunity_id': self.id,
                                  'default_partner_invoice_id': self.agency_id.id})
        return action
