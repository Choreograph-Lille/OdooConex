# -*- coding: utf-8 -*-

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    role_ids = fields.One2many('res.partner.role', 'partner_id', 'Roles')
    country_base = fields.Selection([('uk', 'UK'), ('fr', 'FR')], 'Country Base', default='fr')
    category_name = fields.Char('Category Name')
    last_revival_date = fields.Date('Last Revival Date')
    last_transaction_date = fields.Date('Last Transaction Date')
    data_destruction_date = fields.Date('Data Destruction Date')
    contract_update_date = fields.Date('Contract Update Date')
    rescission_date = fields.Date('Rescission Date')
    base_entry_date = fields.Date('Base Entry Date')
    last_conexup_date = fields.Date('Last Conexup Date')
    last_receipt_date = fields.Date('Last Receipt Date')
    first_contract_date = fields.Date('First Contract Date')
    dpo = fields.Boolean('DPO')
    update_frequency = fields.Char('Update Frequency')
    catalogue_ids = fields.Many2many('res.partner.catalogue', 'res_partner_catalogue_rel', 'partner_id', 'catalogue_id', 'Catalogues')
    private_title = fields.Char('Private Title')
    contract_version = fields.Char('Contract Version')
