# -*- coding: utf-8 -*-
from odoo import fields, models
from odoo.tools.misc import format_datetime

FORMAT_DATE_TIME = 'dd/MM/yyyy HH:mm'
FORMAT_DATE = 'dd/MM/yyyy'


class AuditlogReport(models.TransientModel):
    _name = 'auditlog.report.wizard'

    is_period = fields.Boolean('Period')
    start_date = fields.Date()
    end_date = fields.Date()
    ir_action_report_id = fields.Many2one('ir.actions.report', 'Rule')

    def export(self):
        rule_report_ids = [
            self.env.ref('choreograph_auditlog.action_report_sox_role_changing'),
            self.env.ref('choreograph_auditlog.action_report_res_partner_rib')
        ]
        report_data_map = {
            rule_report_ids[0]: self._data_auditlog_log,
            rule_report_ids[1]: self._data_auditlog_log,
            self.env.ref('choreograph_auditlog.action_report_user_roles_and_right'): self._data_rights_and_roles,
            self.env.ref('choreograph_auditlog.action_report_sox_role_permissions'): self._data_user_sox_roles,
            self.env.ref('choreograph_auditlog.action_report_supplier_bank_details'): self._data_supplier_bank_details,
            self.env.ref('choreograph_auditlog.action_report_accounting'): self._data_accounting,
            self.env.ref('choreograph_auditlog.action_report_quote_purchase_order'): self._data_quote_po
        }
        report_data_func = report_data_map.get(self.ir_action_report_id)
        if not report_data_func:
            return
        if self.ir_action_report_id in rule_report_ids:
            fields_check = None
            partner_report = self.ir_action_report_id == rule_report_ids[1]
            if partner_report:
                fields_check = ['property_account_position_id', 'siret']
            data = self._data_auditlog_log(fields_check)
            if partner_report:
                end_date = self.end_date if self.is_period else self.start_date
                res_partner_bank_logs = self.env['auditlog.log.line'].search([
                    ('create_date', '>=', self.start_date),
                    ('create_date', '<=', end_date),
                    ('field_id', '=', self.env.ref('base.field_res_partner_bank__acc_number').id)
                ])
                for line in res_partner_bank_logs:
                    display_name = self.env[line.log_id.model_id.model].browse(line.log_id.res_id).display_name
                    data['logs'].append({
                        'id': line.log_id.id,
                        'user': line.log_id.user_id.name,
                        'object': line.log_id.model_id.name,
                        'create_date': line.log_id.create_date,
                        'diplay_name': display_name,
                        'method': line.log_id.method,
                        'lines': [
                            {
                                'old_value_text': line.old_value_text,
                                'new_value_text': line.new_value_text,
                                'field_name': line.field_name,
                                'field_description': line.field_description,
                                'create_date': line.create_date,
                                'create_date_formatted': format_datetime(self.env, line.create_date, dt_format=FORMAT_DATE_TIME)
                            }
                        ]})
            sorted_data = sorted(data['logs'], key=lambda item: item['create_date'])
            data['logs'] = sorted_data
        else:
            data = report_data_func()
        data.update({
            'end_date': self.end_date.strftime('%D') if self.end_date else None,
            'start_date': self.start_date.strftime('%D') if self.start_date else None,
        })
        return self.ir_action_report_id.report_action(None, data=data)

    def _data_auditlog_log(self, check_fields=None):
        role_model_id = self.ir_action_report_id.auditlog_model_id.id
        end_date = self.end_date if self.is_period else self.start_date
        logs_ids = self.env['auditlog.log'].search([
            ('create_date', '>=', self.start_date),
            ('create_date', '<=', end_date),
            ('model_id', '=', role_model_id)
        ])
        data = {
            'logs': []
        }
        for log_id in logs_ids:
            lines = log_id.line_ids.filtered(lambda item: not check_fields or item.field_name in check_fields).mapped(lambda line: {
                'old_value_text': line.old_value_text,
                'new_value_text': line.new_value_text,
                'field_name': line.field_name,
                'field_description': line.field_description,
                'create_date': line.create_date,
                'create_date_formatted': format_datetime(self.env, line.create_date, dt_format=FORMAT_DATE_TIME),
            })
            display_name = self.env[log_id.model_id.model].browse(log_id.res_id).display_name
            data['logs'].append({
                'id': log_id.id,
                'display_name': display_name,
                'user': log_id.user_id.name,
                'object': log_id.model_id.name,
                'create_date': log_id.create_date,
                'method': log_id.method,
                'lines': lines
            })
        return data

    def _data_rights_and_roles(self):
        user_ids = self.env['res.users'].search([('share', '=', False)])
        datas = {
            'users': [],
        }
        for user_id in user_ids:
            user_detail = {'name': user_id.name, 'roles': []}
            role_line_ids = user_id.role_line_ids
            for line_id in role_line_ids:
                role_detail = {
                    'name': line_id.role_id.name,
                    'date_from': line_id.date_from,
                    'access': line_id.role_id.model_access_ids.mapped(lambda access: {
                        'object': access.model_id.name,
                        'read': access.perm_read,
                        'write': access.perm_write,
                        'unlink': access.perm_unlink,
                        'create': access.perm_create
                    })
                }
                user_detail['roles'].append(role_detail)
            datas['users'].append(user_detail)
        return datas

    def _data_user_sox_roles(self):
        user_ids = self.env['res.users'].search([('share', '=', False)])
        data = {'users': []}
        for user_id in user_ids:
            data['users'].append({
                'user': user_id.name,
                'groups': user_id.role_line_ids.mapped('role_id').mapped('name')
            })
        return data

    def _data_supplier_bank_details(self):
        partner_bank_ids = self.env['res.partner.bank'].search([])
        data = {'banks': []}
        for partner_bank_id in partner_bank_ids:
            data['banks'].append({
                'name': partner_bank_id.bank_id.name,
                'bic': partner_bank_id.bank_id.bic,
                'iban': partner_bank_id.acc_number,
                'exempt_vat': partner_bank_id.partner_id.property_account_position_id.name,
                'siret': partner_bank_id.partner_id.siret
            })
        return data

    def _data_accounting(self):
        end_date = self.end_date if self.is_period else self.start_date
        log_line_ids = self.env['auditlog.log.line'].search([
            ('field_name', '=', 'state'),
            ('new_value_text', '=', 'posted'),
            ('log_id.model_id', '=', self.env.ref('account.model_account_move').id),
            ('create_date', '>=', self.start_date),
            ('create_date', '<=', end_date)
        ])
        move_ids = self.env['account.move'].search([
            ('state', '=', 'posted'),
            ('id', 'in', log_line_ids.mapped('log_id.res_id'))
        ])
        data = {
            'accounts': []
        }
        for move_id in move_ids:
            log_line_id = log_line_ids.filtered(lambda l: l.log_id.res_id == move_id.id).sorted(
                lambda item: item.create_date, reverse=True)[0]
            data['accounts'].append({
                'client': move_id.partner_id.name,
                'invoice_date': format_datetime(self.env, log_line_id.create_date, dt_format=FORMAT_DATE),
                'credit_note_number': move_id.name,
                'commercial': move_id.invoice_user_id.name,
                'origin_document': move_id.invoice_origin,
                'subtotal': move_id.amount_total,
                'creator': move_id.create_uid.name,
                'validator': log_line_id.log_id.user_id.name if log_line_id else None,
                'validation_date': format_datetime(self.env, log_line_id.create_date, dt_format=FORMAT_DATE_TIME),
                'comment': '',
            })
        return data

    def _data_quote_po(self):
        end_date = self.end_date if self.is_period else self.start_date
        log_line_ids = self.env['auditlog.log.line'].search([
            ('field_name', '=', 'sox'),
            ('new_value_text', '=', 'True'),
            ('log_id.model_id', '=', self.env.ref('sale.model_sale_order').id),
            ('create_date', '>=', self.start_date),
            ('create_date', '<=', end_date)
        ])
        order_ids = self.env['sale.order'].search([
            ('state', '=', 'sale'),
            ('sox', '=', True),
            ('id', 'in', log_line_ids.mapped('log_id.res_id'))
        ])
        data = {
            'orders': []
        }
        for order in order_ids:
            log_line_id = log_line_ids.filtered(lambda l: l.log_id.res_id == order.id).sorted(
                lambda item: item.create_date, reverse=True)[0]
            data['orders'].append({
                'author': log_line_id.log_id.user_id.name,
                'sox_date': format_datetime(self.env, log_line_id.create_date, dt_format=FORMAT_DATE_TIME),
                'delivery_date': format_datetime(self.env, order.commitment_date, dt_format=FORMAT_DATE_TIME),
                'name': order.name
            })
        return data
