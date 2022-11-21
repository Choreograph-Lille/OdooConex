# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    role_ids = fields.One2many('res.partner.choreograph.role', 'partner_id', string='Roles')

    # fields from studio
    activity = fields.Selection([
        ('press', 'Press'),
        ('charity', 'Charity'),
        ('bank', 'Bank / Insurance'),
        ('leisure', 'Leisure'),
    ], string='Activity sector')
    country_base = fields.Selection([
        ('uk', 'UK'),
        ('fr', 'FR'),
    ], string='Country base')
    category_name = fields.Char('Category name')
    last_revival_date = fields.Date('Last revival date')
    last_transaction_date = fields.Date('Last transaction date')
    data_destruction_date = fields.Date('Data destruction date')
    contract_update_date = fields.Date('Contract update date')
    rescission_date = fields.Date('Rescission date')
    base_entry_date = fields.Date('Base entry date')
    last_conexup_date = fields.Date('Last Conexup date')
    last_receipt_date = fields.Date('Last receipt date')
    first_contract_date = fields.Date('First contract date')
    dpo = fields.Boolean('DPO')
    sale_team = fields.Char('Sale team')
    update_frequency = fields.Char('Update frequency')
    catalogue_ids = fields.Many2many('res.partner.catalogue', string='Catalogue')
    private_title = fields.Char('Private title')


class ResPartnerCatalogue(models.Model):
    _name = 'res.partner.catalogue'

    name = fields.Char('Name')
