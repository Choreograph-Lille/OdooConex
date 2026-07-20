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
    sage_sale_file_date = fields.Datetime(
    string="File date",
    config_parameter='choreograph_sage_sale_account.sage_file_date',
    help="Leave empty to use today's date",
    )