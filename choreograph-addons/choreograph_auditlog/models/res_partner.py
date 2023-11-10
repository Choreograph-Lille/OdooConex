from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_account_position = fields.Char(related='property_account_position_id.name', store=True)
    banks = fields.Char(compute='compute_banks', store=True)

    @api.depends('bank_ids')
    def compute_banks(self):
        for rec in self:
            banks = []
            for bank in rec.bank_ids:
                bank_name = bank.bank_id.name if bank.bank_id else '-'
                banks.append( bank_name + '/' + bank.acc_number)
            rec.banks = ', '.join(banks)
