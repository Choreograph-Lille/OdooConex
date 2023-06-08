from odoo import models


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _check_suggestion(self, value):
        check_value = [
            'partner_id' in self and self.partner_id._name == 'res.partner' and self.partner_id.id == value[0],
            'user_ids' in self and self.user_ids._name == 'res.users' and value[0] in self.user_ids.partner_id.ids
        ]
        if self._name == 'res.partner':
            check_value.extend([
                self.parent_id.id == value[0],
                self.user_id.partner_id.id == value[0],
                self.id == value[0]
            ])
        return any(check_value)

    def _get_mail_thread_data(self, request_list):
        res = super()._get_mail_thread_data(request_list)
        if 'suggestedRecipients' not in request_list:
            return res
        if self.env.company.disable_followers:
            suggestedRecipients = [item for item in res['suggestedRecipients'] if not self._check_suggestion(item)]
            res['suggestedRecipients'] = suggestedRecipients
        return res
