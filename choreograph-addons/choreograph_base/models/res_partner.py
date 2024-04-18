from odoo import fields, models, api


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
    property_product_pricelist = fields.Many2one(comodel_name='product.pricelist', tracking=10, company_dependent=False, store=True)
    property_supplier_payment_term_id = fields.Many2one(comodel_name='account.payment.term', tracking=10, company_dependent=False)
    property_purchase_currency_id = fields.Many2one(comodel_name='res.currency', tracking=10, company_dependent=False)
    property_account_position_id = fields.Many2one(comodel_name='account.fiscal.position', tracking=10, company_dependent=False)
    property_payment_term_id = fields.Many2one('account.payment.term', company_dependent=False)
    property_account_receivable_id = fields.Many2one(comodel_name='account.account', tracking=10)
    property_account_payable_id = fields.Many2one(comodel_name='account.account', tracking=10)
    receipt_reminder_email = fields.Boolean(tracking=10)
    followup_next_action_date = fields.Date(company_dependent=False)
    followup_responsible_id = fields.Many2one(comodel_name='res.users', company_dependent=False)

    def _valid_field_parameter(self, field, name):
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    @api.model_create_multi
    def create(self, values):
        for value in values:
            if value.get('is_company'):
                next_ref = self.env['ir.sequence'].next_by_code('res.partner.company.ref')
                value.update({
                    'ref': next_ref
                })
        return super(ResPartner, self).create(values)

    def get_base_url(self):
        result = super(ResPartner, self).get_base_url()
        if self.user_ids and self.user_ids[0].share:
            return self.env["ir.config_parameter"].sudo().get_param("web.mymodel.url", result)
        return result
