# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    role_ids = fields.One2many('res.partner.role', 'partner_id', 'Roles')
    country_base = fields.Selection([('uk', 'UK'), ('fr', 'FR')], 'Country Base', default='fr', tracking=10)
    category_name = fields.Char(tracking=10)
    last_revival_date = fields.Date('Last Revival Date', tracking=10)
    last_transaction_date = fields.Date('Last Transaction Date', tracking=10)
    data_destruction_date = fields.Date('Data Destruction Date', tracking=10)
    contract_update_date = fields.Date('Contract Update Date', tracking=10)
    rescission_date = fields.Date('Rescission Date', tracking=10)
    base_entry_date = fields.Date('Base Entry Date', tracking=10)
    last_conexup_date = fields.Date('Last Conexup Date', tracking=10)
    last_receipt_date = fields.Date('Last Receipt Date', tracking=10)
    first_contract_date = fields.Date('First Contract Date', tracking=10)
    is_dpo = fields.Boolean('DPO')
    update_frequency = fields.Char('Update Frequency', tracking=10)
    catalogue_ids = fields.Many2many('res.partner.catalogue', 'res_partner_catalogue_rel',
                                     'partner_id', 'catalogue_id', 'Catalogues')
    private_title = fields.Boolean('Private Title', tracking=10)
    agency_id = fields.Many2one('res.partner', 'Agency', ondelete='restrict', index=True, tracking=10)
    industry_id = fields.Many2one('res.partner.industry', 'Activity area', tracking=10)
