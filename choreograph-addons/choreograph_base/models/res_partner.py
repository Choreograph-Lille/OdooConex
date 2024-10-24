from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    name = fields.Char(tracking=100)
    mobile = fields.Char(tracking=10)
    website = fields.Char(tracking=10)
    street = fields.Char(tracking=10)
    street2 = fields.Char(tracking=10)
    city = fields.Char(tracking=10)
    zip = fields.Char(tracking=10)
    company_registry = fields.Char(tracking=10)
    ref = fields.Char(tracking=10)
    siret = fields.Char(tracking=10)
    company_type = fields.Selection(tracking=10)
    lang = fields.Selection(tracking=10)
    state_id = fields.Many2one(tracking=10)
    country_id = fields.Many2one(tracking=10)
    team_id = fields.Many2one(tracking=10)
    website_id = fields.Many2one(tracking=10)
    property_payment_term_id = fields.Many2one(comodel_name='account.payment.term', tracking=10)
    property_product_pricelist = fields.Many2one(comodel_name='product.pricelist', tracking=10)
    property_supplier_payment_term_id = fields.Many2one(comodel_name='account.payment.term', tracking=10)
    property_purchase_currency_id = fields.Many2one(comodel_name='res.currency', tracking=10)
    property_account_position_id = fields.Many2one(comodel_name='account.fiscal.position', tracking=10)
    property_account_receivable_id = fields.Many2one(comodel_name='account.account', tracking=10)
    property_account_payable_id = fields.Many2one(comodel_name='account.account', tracking=10)
    receipt_reminder_email = fields.Boolean(tracking=10)

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)
