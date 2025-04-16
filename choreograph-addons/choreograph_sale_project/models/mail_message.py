from odoo import _, api, models

X2MANY_MODEL = [
    'operation.condition',
    'operation.segment',
    'operation.provider.delivery'
]


class MailMessage(models.Model):
    _inherit = 'mail.message'

    def _message_format(self, fnames, format_reply=True, legacy=False):
        """Display operation name beside task name in discussion"""
        vals_list = super()._message_format(fnames, format_reply, legacy)
        for vals in vals_list:
            message_sudo = self.browse(vals['id']).sudo().with_prefetch(self.ids)
            if message_sudo.model and message_sudo.res_id and message_sudo.model == "project.task":
                project_id = self.env["project.task"].browse(message_sudo.res_id).sudo().project_id
                vals["record_name"] += f' | {project_id.name}'
                if project_id.partner_id:
                    vals["record_name"] += f' - {project_id.partner_id.name}'
        return vals_list

    @api.model_create_multi
    def create(self, values_list):
        res = super().create(values_list)
        methodology_model_name = 'methodology.methodology'
        if all(model_name for model_name in set(res.mapped('model')) if model_name == methodology_model_name) and not self._context.get('is_copy', False):
            methodology_id = self.env[methodology_model_name].browse(res.mapped('res_id')[0])
            for message_id in res:
                message_id.with_context(is_copy=True).copy({
                    'model': methodology_id.order_id._name,
                    'res_id': methodology_id.order_id.id,
                    'tracking_value_ids': [(6, 0, message_id.tracking_value_ids.ids)],
                })
        return res

