from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sale_warn = fields.Selection(tracking=10)
    sale_warn_msg = fields.Text(tracking=10)
