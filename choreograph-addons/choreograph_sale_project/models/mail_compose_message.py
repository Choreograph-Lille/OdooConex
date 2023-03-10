# -*- coding: utf-8 -*-

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail(self, auto_commit=False):
        res = super()._action_send_mail()
        if self.env.context.get('operation_email_process'):
            self.env['mail.mail'].search([('message_id', '=', res[1].message_id)]).write({
                'res_id': False
            })
        return res
