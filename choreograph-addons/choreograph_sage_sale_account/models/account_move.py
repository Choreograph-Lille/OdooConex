# -*- coding: utf-8 -*-

from odoo import api, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_sage_file_config(self):
        if self.env.context.get('move_type') != 'out_invoice':
            return super()._get_sage_file_config()
        config_parameter = self.env['ir.config_parameter'].sudo()
        return (
            config_parameter.get_param('choreograph_sage_sale_account.prefix') or False,
            config_parameter.get_param('choreograph_sage_sale_account.suffix') or False,
            config_parameter.get_param('choreograph_sage_sale_account.sage_file_date') or False,
        )

    @api.model
    def import_account_move_out_invoice(self):
        return self._run_sage_import('out_invoice', 'sale')
