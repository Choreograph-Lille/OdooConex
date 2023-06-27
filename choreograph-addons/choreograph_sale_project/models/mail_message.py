import copy
from odoo import _, api, models

X2MANY_MODEL = [
    'operation.condition',
    'operation.segment',
    'operation.provider.delivery'
]


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model_create_multi
    def create(self, values_list):
        order_obj = self.env['sale.order']
        operation_value_extend = []
        subtype_id = self.env.ref('mail.mt_note').id
        for values in values_list:
            if values.get('is_internal', False) and values.get('subtype_id', False) == subtype_id:
                if values.get('model', False) in X2MANY_MODEL:
                    vals = self.so_x2many_fields_to_project(values)
                    if vals:
                        values.update(vals)
                if values.get('model', False) == 'sale.order':
                    order_id = order_obj.browse(values['res_id'])
                    if order_id and order_id.project_ids:
                        order_tracking_value_ids, operation_value = self.so_basic_fields_to_project(values, order_id)
                        values['tracking_value_ids'] = order_tracking_value_ids
                        operation_value_extend.append(operation_value)
        values_list.extend(operation_value_extend)
        return super().create(values_list)

    @api.model
    def so_x2many_fields_to_project(self, values: dict):
        line_name = {
            'operation.condition': _('Condition/Exclusion line : %s'),
            'operation.segment': _('Segment line : %s'),
            'operation.provider.delivery': _('Presta Delivery : %s'),
        }
        line = self.env[values['model']].browse(values['res_id'])
        body = None
        operation_id = line.order_id.project_ids[0]
        if not values.get('body', False):
            body = line_name[values['model']]
            body = body % line.sequence
        return {
            'model': 'project.project',
            'res_id': operation_id.id,
            'body': body or values['body']
        } if operation_id.stage_id.stage_number != '10' else None

    @api.model
    def so_basic_fields_to_project(self, values: dict, order_id) -> tuple:
        operation_id = order_id.project_ids[0]
        order_tracking_value_ids = []
        operation_tracking_value_ids = []
        order_obj = self.env['sale.order']
        sale_order_field_list = order_obj.get_mail_field_to_operation()
        valid_stage = order_id.project_ids.stage_id.stage_number != '10'
        for tracking_value_id in values.get('tracking_value_ids', []):
            field_id = tracking_value_id[2]['field']
            if field_id in sale_order_field_list:
                if valid_stage:
                    if field_id in order_obj.get_sms_campaign_field():
                        tracking_value_id[2]['field_desc'] += ' - SMS'
                    if field_id in order_obj.get_email_campaign_field():
                        tracking_value_id[2]['field_desc'] += ' - EMAIL'
                    operation_tracking_value_ids.append(tracking_value_id)
            else:
                order_tracking_value_ids.append(tracking_value_id)
        operation_value = copy.deepcopy(values)
        operation_value.update({
            'tracking_value_ids': operation_tracking_value_ids,
            'res_id': operation_id.id,
            'model': 'project.project'
        })
        return order_tracking_value_ids, operation_value
