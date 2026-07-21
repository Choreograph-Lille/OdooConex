# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sage_file_prefix = fields.Char(string="Prefix", config_parameter='choreograph_sage_purchase_account.prefix')
    sage_file_suffix = fields.Char(string="Suffix", config_parameter='choreograph_sage_purchase_account.suffix')
    sage_file_date = fields.Datetime(string="Date import", config_parameter='choreograph_sage_purchase_account.sage_file_date')
    sage_purchase_default_journal_id = fields.Many2one('account.journal',
                                                       config_parameter='choreograph_sage_purchase_account.purchase_default_journal_id',
                                                       domain="[('type', 'in', ('bank', 'cash'))]"
                                                       )