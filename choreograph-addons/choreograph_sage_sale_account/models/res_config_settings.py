from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sage_sale_file_prefix = fields.Char(
        string="Prefix",
        config_parameter='choreograph_sage_sale_account.prefix',
    )
    sage_sale_file_suffix = fields.Char(
        string="Suffix",
        config_parameter='choreograph_sage_sale_account.suffix',
    )