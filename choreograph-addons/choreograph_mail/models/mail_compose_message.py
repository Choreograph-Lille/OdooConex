# -*- coding: utf-8 -*-

from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

    def _action_send_mail(self, auto_commit=False):
        self = self.with_context(compose_partners=self.partner_ids)
        return super(MailComposeMessage, self)._action_send_mail(auto_commit)
