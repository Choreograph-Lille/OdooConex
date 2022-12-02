# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sox = fields.Boolean('SOX')
    activity_sector = fields.Selection([
        ('press', 'Press'),
        ('charity', 'Charity'),
        ('bank', 'Bank / Insurance'),
        ('leisure', 'Leisure'),
    ], string='Activity sector', related='partner_id.activity')
    category_name = fields.Char('Category name', related='partner_id.category_name')
    agency_id = fields.Many2one('res.partner', string='Agency')

    def action_new_quotation(self):
        action = self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        action['context'] = self._prepare_opportunity_quotation_context()
        action['context']['search_default_opportunity_id'] = self.id
        action['context']['default_partner_invoice_id'] = self.agency_id.id
        return action

    @api.model
    def create(self, vals):
        res = super(CrmLead, self).create(vals)
        self.update_name()
        return res

    def write(self, vals):
        result = super(CrmLead, self).write(vals)
        if 'contact_name' in vals or 'name' in vals:
            self.update_name()
        return result

    def update_name(self):
        for rec in self:
            if rec.contact_name in rec.name:
                return True
            else:
                rec.name = rec.contact_name + ' - ' + rec.name
