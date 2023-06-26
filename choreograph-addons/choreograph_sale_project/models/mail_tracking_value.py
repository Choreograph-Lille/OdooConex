# -*- coding: utf-8 -*-

from odoo import models


class MailTracking(models.Model):
    _inherit = "mail.tracking.value"

    def _compute_field_groups(self):
        for tracking in self:
            model = self.env[tracking.mail_message_id.model]
            field = model._fields.get(tracking.field.name)
            tracking.field_groups = field.groups if field else "base.group_user"