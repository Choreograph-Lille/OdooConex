# -*- coding: utf-8 -*-

from odoo import api, models

MODEL_TO_UNFOLLOW = [
    'sale.order',
    'account.move',
    'project.project',
    'purchase.order'
]


class MailFollowers(models.Model):
    _inherit = 'mail.followers'

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('res_model', False) in MODEL_TO_UNFOLLOW and values.get('res_id', False):
                source_id = self.env[values['res_model']].browse(values['res_id'])
                if source_id and 'partner_id' in source_id and source_id.partner_id and source_id.partner_id.id == values['partner_id']:
                    vals_list.remove(values)
        res = super(MailFollowers, self).create(vals_list)
        res._invalidate_documents(vals_list)
        return res

    @api.model
    def delete_mail_followers(self):
        for model in MODEL_TO_UNFOLLOW:
            record_ids = self.env['mail.followers'].search([('res_model', '=', model), ('partner_id', '>', 4)])
            for record in record_ids:
                source_id = self.env[record.res_model].search([
                    ('id', '=', record.res_id),
                    ('partner_id', '=', record.partner_id.id)
                ])
                if source_id:
                    record.unlink()
