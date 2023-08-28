# -*- coding: utf-8 -*-

from odoo import models, api


class MailTracking(models.Model):
    _inherit = "mail.tracking.value"

    @api.model
    def create_tracking_values(self, initial_value, new_value, col_name, col_info, tracking_sequence, model_name):
        """
            allow tracking many2many field order_ids from operation.condition
        """
        res = super(MailTracking, self).create_tracking_values(initial_value, new_value, col_name, col_info,
                                                               tracking_sequence, model_name)
        if not res and model_name == 'operation.condition' and col_name == "order_ids":

            field = self.env['ir.model.fields']._get(model_name, col_name)
            if not field:
                return

            values = {'field': field.id, 'field_desc': col_info['string'], 'field_type': col_info['type'],
                      'tracking_sequence': tracking_sequence}

            if col_info['type'] == 'many2many':
                values.update({
                    'old_value_char': initial_value and ', '.join(
                        i.sudo().name_get()[0][1] for i in initial_value) or '',
                    'new_value_char': new_value and ', '.join(i.sudo().name_get()[0][1] for i in new_value) or ''
                })
                return values
        return res
