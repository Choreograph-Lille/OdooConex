# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    role_ids = fields.One2many('res.partner.role', 'partner_id', 'Roles', tracking=True)
    country_base = fields.Selection([('uk', 'UK'), ('fr', 'FR')], 'Country Base', default='fr', tracking=True)
    category_name = fields.Char(tracking=True)
    last_revival_date = fields.Date('Last Revival Date', tracking=True)
    last_transaction_date = fields.Date('Last Transaction Date', tracking=True)
    data_destruction_date = fields.Date('Data Destruction Date', tracking=True)
    contract_update_date = fields.Date('Contract Update Date', tracking=True)
    rescission_date = fields.Date('Rescission Date', tracking=True)
    base_entry_date = fields.Date('Base Entry Date', tracking=True)
    last_conexup_date = fields.Date('Last Conexup Date', tracking=True)
    last_receipt_date = fields.Date('Last Receipt Date', tracking=True)
    first_contract_date = fields.Date('First Contract Date', tracking=True)
    is_dpo = fields.Boolean('DPO', tracking=True)
    update_frequency = fields.Char('Update Frequency', tracking=True)
    catalogue_ids = fields.Many2many('res.partner.catalogue', 'res_partner_catalogue_rel',
                                     'partner_id', 'catalogue_id', 'Catalogues', tracking=True)
    private_title = fields.Boolean('Private Title', tracking=True)
    agency_id = fields.Many2one('res.partner', 'Agency', ondelete='restrict', index=True, tracking=True)
    industry_id = fields.Many2one('res.partner.industry', 'Activity area', tracking=True)
    function = fields.Char(string='Job Position', tracking=True)
