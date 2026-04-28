from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    new_address = fields.Html()
    siren = fields.Char(string="SIREN")

