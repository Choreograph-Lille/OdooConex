# -*- coding: utf-8 -*-

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail(self, auto_commit=False):
        res = super()._action_send_mail()
        if self.env.context.get('operation_email_process'):
            self.action_operation_email_process(res)
        return res

    def action_operation_email_process(self, res):
        order = self.env[res[1].model].browse(res[1].res_id)
        self.env['mail.mail'].search([('message_id', '=', res[1].message_id)]).write({
            'res_id': False
        })
        order.project_ids[0].livery_project()
