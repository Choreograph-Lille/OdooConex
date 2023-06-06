# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    groups_id = fields.Many2many(default=False)
    bool_sms = fields.Boolean("SMS")
    bool_print = fields.Boolean("Print")
    bool_email = fields.Boolean("Email?")
    default_sms = fields.Boolean()
    default_print = fields.Boolean()
    default_email = fields.Boolean()
    customer_ids = fields.Many2many('res.partner', 'res_users_customer_rel',
                                    'user_id', 'partner_id', string='Customers')
    is_user_profile  = fields.Boolean()

    @api.onchange('default_sms')
    def onchange_default_sms(self):
        if self.default_sms:
            self.default_print = False
            self.default_email = False
            self.bool_sms = True

    @api.onchange('default_print')
    def onchange_default_print(self):
        if self.default_print:
            self.default_sms = False
            self.default_email = False
            self.bool_print = True

    @api.onchange('default_email')
    def onchange_default_email(self):
        if self.default_email:
            self.default_sms = False
            self.default_print = False
            self.bool_email = True

    @api.onchange('bool_sms')
    def onchange_bool_sms(self):
        if not self.bool_sms:
            self.default_sms = False

    @api.onchange('bool_print')
    def onchange_bool_print(self):
        if not self.bool_print:
            self.default_print = False

    @api.onchange('bool_email')
    def onchange_bool_email(self):
        if not self.bool_email:
            self.default_email = False

    def get_canal(self):
        self.ensure_one()
        result = []
        if self.bool_sms:
            result.append(('SMS', "1" if self.default_sms else "0"))
        if self.bool_print:
            result.append(('Print', "1" if self.default_print else "0"))
        if self.bool_email:
            result.append(('Email', "1" if self.default_email else "0"))
        return result
