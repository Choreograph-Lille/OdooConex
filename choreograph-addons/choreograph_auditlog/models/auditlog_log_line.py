from odoo import api, models


class AuditlogLogLine(models.Model):
    _inherit = 'auditlog.log.line'

    @api.model
    def find_user_id(self, field_name, res_id, new_value_text):
        log_id = self.search([
            ('log_id.res_id', '=', res_id),
            ('field_name', '=', field_name),
            ('new_value_text', '=', new_value_text)
        ], order='create_date desc', limit=1)
        return log_id.log_id.user_id.name if log_id else None

    def get_record(self):
        return self.env[self.log_id.model_id.model].browse(self.log_id.res_id)
