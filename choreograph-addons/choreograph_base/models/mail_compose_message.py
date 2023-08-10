# -*- coding: utf-8 -*-
from odoo import models


class MailComposeMessage(models.TransientModel):
	_inherit = "mail.compose.message"

	def _action_send_mail(self, auto_commit=False):
		user_url = False
		compose_partners = self.partner_ids
		if self.template_id and self.template_id.user_url:
			user_url = self.template_id.user_url
		else:
			partners = self.partner_ids
			users = self.env['res.users'].sudo().search([('partner_id', 'in', partners.ids)])
			if any(user.is_standard() or user.is_validator() for user in users):
				user_url = 'mymodel'
		return super(MailComposeMessage, self.with_context(user_url=user_url, compose_partners=compose_partners))._action_send_mail(auto_commit)

