from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    new_address = fields.Html()
    siren = fields.Char(string="SIREN")
    electronic_address = fields.Char(string="Electronic Address")
    
    def get_electronic_address(self):
        """Return the electronic address of the company or its partner if not set."""
        self.ensure_one()
        return self.electronic_address or self.partner_id.electronic_address
