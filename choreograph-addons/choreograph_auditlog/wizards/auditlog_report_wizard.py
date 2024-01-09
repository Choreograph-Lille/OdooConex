# -*- coding: utf-8 -*-
import json
import re

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.misc import format_datetime, format_date, formatLang

FORMAT_DATE_TIME = 'dd/MM/yyyy HH:mm'
FORMAT_DATE = 'dd/MM/yyyy'


class AuditlogReport(models.TransientModel):
    _name = 'auditlog.report.wizard'
    _description = "Audit Log Report Assistant"

    is_period = fields.Boolean('Period')
    start_date = fields.Date('Date')
    end_date = fields.Date()
    ir_action_report_id = fields.Many2one('ir.actions.report', 'Rule')
    user_ids = fields.Many2many('res.users')
    is_extracts_from_supplier = fields.Boolean(compute='_compute_is_extracts_from_supplier', store=True)

    @api.depends('ir_action_report_id')
    def _compute_is_extracts_from_supplier(self):
        for audit in self:
            extract_supplier = self.env.ref('choreograph_auditlog.action_report_extracts_from_suppliers', raise_if_not_found=False)
            is_extracts_from_supplier = False
            if audit.ir_action_report_id == extract_supplier:
                is_extracts_from_supplier = True
            audit.is_extracts_from_supplier = is_extracts_from_supplier

    @api.constrains('start_date', 'end_date', 'is_period')
    def _check_date(self):
        for report in self:
            if report.is_period and report.start_date > report.end_date:
                raise ValidationError(_('The start date cannot be greater than the end date'))

    def export(self):
        report_data_map = {
            self.env.ref('choreograph_auditlog.action_report_sox_role_changing'): self._data_sox_role_changing,
            self.env.ref('choreograph_auditlog.action_report_res_partner_rib'): self._data_partner_rib,
            self.env.ref('choreograph_auditlog.action_report_extracts_from_suppliers'): self._data_supplier_extract,
            self.env.ref('choreograph_auditlog.action_report_user_roles_and_right'): self._data_rights_and_roles,
            self.env.ref('choreograph_auditlog.action_report_sox_role_permissions'): self._data_user_sox_roles,
            self.env.ref('choreograph_auditlog.action_report_supplier_bank_details'): self._data_supplier_bank_details,
            self.env.ref('choreograph_auditlog.action_report_accounting'): self._data_accounting,
            self.env.ref('choreograph_auditlog.action_report_quote_purchase_order'): self._data_quote_po,
            self.env.ref('choreograph_auditlog.action_report_purchase_closing'): self._data_purchase_closing,
        }
        report_data_func = report_data_map.get(self.ir_action_report_id)
        if not report_data_func:
            return
        data = report_data_func()
        data.update({
            'end_date': format_date(self.env, self.end_date, FORMAT_DATE) if self.end_date else None,
            'start_date': format_date(self.env, self.start_date, FORMAT_DATE) if self.start_date else None,
            'is_periode': self.is_period,
            'sequence': self.env['ir.sequence'].next_by_code('auditlog.report.wizard')
        })
        return self.ir_action_report_id.report_action(None, data=data)

    def get_log_lines(self, model, fields=[], method='', is_supplier_extraction=False):
        end_date = self.end_date if self.is_period else self.start_date
        domain = [
            ('create_date', '>=', self.start_date),
            ('create_date', '<=', end_date),
            ('log_id.model_id', '=', model.id),
        ]
        if fields:
            domain.append(('field_name', 'in', fields))
        if self.user_ids:
            domain.append(('log_id.user_id', 'in', self.user_ids.ids))
        if method:
            domain.append(('log_id.method', '=', method))
        if is_supplier_extraction:
            domain.append(('log_id.res_id', 'in', self.env['res.partner'].search([('supplier_rank', '!=', 0)]).ids))
        return self.env['auditlog.log.line'].search(domain)

    def prepare_log_line_data(self, line, display_name, is_data_sox_role_changing=False):
        """
        Return a dict of datas used in the report
        :param line: the log line
        :param display_name: name of the record
        :param is_data_sox_role_changing: if True, take only the difference between old and new values
        :return: dict
        """
        old_value = line.old_value_text
        new_value = line.new_value_text
        if is_data_sox_role_changing:
            old_value_list = old_value.split(',')
            new_value_list = new_value.split(',')
            old_value = ', '.join(list(set(old_value_list) - set(new_value_list)))
            new_value = ', '.join(list(set(new_value_list) - set(old_value_list)))
        return {
            'id': line.log_id.id,
            'display_name': display_name,
            'user': line.log_id.user_id.name,
            'object': line.log_id.model_id.name,
            'create_date': line.log_id.create_date,
            'method': line.log_id.method,
            'lines': [{
                'old_value_text': old_value,
                'new_value_text': new_value,
                'field_name': line.field_name,
                'field_description': line.field_description,
                'create_date': line.create_date,
                'create_date_formatted': format_datetime(self.env, line.create_date, dt_format=FORMAT_DATE_TIME),
            }]
        }

    def _data_sox_role_changing(self):
        data = {
            'logs': []
        }
        # this should be res.users
        role_model = self.ir_action_report_id.auditlog_model_id
        logs_lines = self.get_log_lines(role_model, ['user_roles'])
        for line in logs_lines:
            record = line.get_record()
            data['logs'].append(self.prepare_log_line_data(line, record.display_name, True))
        return data

    def _data_partner_rib(self):
        data = {
            'logs': []
        }
        # this should be res.partner
        role_model = self.ir_action_report_id.auditlog_model_id
        logs_lines = self.get_log_lines(role_model, ['siret', 'banks'], 'write', True)
        for line in logs_lines:
            record = line.get_record()
            data['logs'].append(self.prepare_log_line_data(line, record.display_name))
        return data

    def _data_supplier_extract(self):
        data = {
            'logs': []
        }
        # this should be res.partner
        role_model = self.ir_action_report_id.auditlog_model_id
        logs_lines = self.get_log_lines(role_model, [], True)
        for line in logs_lines:
            record = line.get_record()
            data['logs'].append(self.prepare_log_line_data(line, record.display_name))
        return data

    def _data_rights_and_roles(self):
        user_ids = self.env['res.users'].search([('share', '=', False)])
        datas = {
            'users': [],
        }
        for user_id in user_ids:
            user_detail = {'name': user_id.name, 'roles': []}
            sox = self.env.ref("base_user_role.ir_module_category_role", raise_if_not_found=False)
            groups_ids = user_id.groups_id.filtered(lambda grp: grp.category_id == sox)
            for group_id in groups_ids:
                details = {
                    'name': group_id.name,
                    'date_from': None,
                    'access': group_id.role_ids.model_access_ids.mapped(lambda access: {
                        'object': access.model_id.name,
                        'read': access.perm_read,
                        'write': access.perm_write,
                        'unlink': access.perm_unlink,
                        'create': access.perm_create
                    })
                }
                user_detail['roles'].append(details)
            datas['users'].append(user_detail)
        return datas

    def _data_user_sox_roles(self):
        user_ids = self.env['res.users'].search([('share', '=', False)])
        data = {'users': []}
        sox = self.env.ref("base_user_role.ir_module_category_role", raise_if_not_found=False)
        for user_id in user_ids:
            data['users'].append({
                'user': user_id.name,
                'groups': user_id.groups_id.filtered(lambda grp: grp.category_id == sox).mapped('name')
            })
        return data

    def _data_supplier_bank_details(self):
        partner_bank_ids = self.env['res.partner.bank'].search([])
        data = {'banks': []}
        for partner_bank_id in partner_bank_ids:
            data['banks'].append({
                'name': partner_bank_id.partner_id.name,
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
            ('move_type', '=', 'out_refund'),
            ('id', 'in', log_line_ids.mapped('log_id.res_id'))
        ])
        data = {
            'accounts': []
        }
        for move_id in move_ids:
            split_ref = move_id.ref.split(',') if move_id.ref else ''
            log_line_id = log_line_ids.filtered(lambda l: l.log_id.res_id == move_id.id).sorted(
                lambda item: item.create_date, reverse=True)[0]
            data['accounts'].append({
                'client': move_id.partner_id.name,
                'invoice_date': format_datetime(self.env, log_line_id.create_date, dt_format=FORMAT_DATE),
                'credit_note_number': move_id.name,
                'commercial': move_id.invoice_user_id.name,
                'origin_document': move_id.reversed_entry_id.name,
                'subtotal': formatLang(self.env, move_id.amount_total),
                'creator': move_id.create_uid.name,
                'validator': log_line_id.log_id.user_id.name if log_line_id else None,
                'validation_date': format_datetime(self.env, log_line_id.create_date, dt_format=FORMAT_DATE_TIME),
                'comment': split_ref[1] if len(split_ref) == 2 else ''
            })
        return data

    def _data_quote_po(self):
        end_date = self.end_date if self.is_period else self.start_date
        order_ids = self.env['sale.order'].search([
            ('state_specific', '=', 'closed_won'),
            ('commitment_date', '>=', self.start_date),
            ('commitment_date', '<=', end_date)
        ])
        data = {
            'orders': []
        }
        for order in order_ids:
            sox_data = self.get_sox_data_for_report(order)
            data['orders'].append({
                'name': order.name,
                'sox': _('Yes') if order.sox else _('No'),
                'author': sox_data.log_id.user_id.name if sox_data and order.sox else '',
                'sox_date': format_datetime(self.env, sox_data.log_id.create_date, dt_format=FORMAT_DATE_TIME) if sox_data and order.sox else '',
                'delivery_date': format_datetime(self.env, order.commitment_date, dt_format=FORMAT_DATE_TIME),
            })
        return data

    def get_sox_data_for_report(self, order):
        role_model = self.ir_action_report_id.auditlog_model_id
        domain = [
            ('log_id.model_id', '=', role_model.id),
            ('log_id.res_id', '=', order.id),
            ('field_name', '=', 'sox')
        ]
        return self.env['auditlog.log.line'].search(domain, order='id desc', limit=1)

    def _data_purchase_closing(self):
        end_date = self.end_date if self.is_period else self.start_date
        order_ids = self.env['sale.order'].search([
            ('state', '=', 'sale'),
            ('date_order', '>=', self.start_date),
            ('date_order', '<=', end_date)
        ]).filtered(lambda o: len(o._get_purchase_orders().ids))
        datas = {
            'orders': []
        }

        def get_approval_entries(res_id, groups):
            entries = self.env['studio.approval.entry'].search([
                ('model', '=', 'purchase.order'),
                ('res_id', '=', res_id),
                ('approved', '=', True),
                ('group_id', 'in', groups)
            ])
            res = entries.mapped('user_id.name')
            return res

        for order_id in order_ids:
            purchase_order_ids = order_id._get_purchase_orders()
            po_list = purchase_order_ids.mapped(lambda po: {
                'purchase': {
                    'po_number': po.name,
                    'supplier': po.partner_id.name,
                    'date_approve': format_date(self.env, po.date_approve, FORMAT_DATE),
                    'date_planned': format_date(self.env, po.date_planned, FORMAT_DATE),
                    'amount': formatLang(self.env, po.amount_untaxed),
                },
                'invoices': po.invoice_ids.mapped(lambda invoice: {
                    'invoice_name': invoice.name,
                    'invoice_date': format_date(self.env, invoice.invoice_date, FORMAT_DATE),
                    'amount': formatLang(self.env, invoice.amount_total),
                    'diff': _('Yes') if invoice.is_gap else _('No')
                }),
                'informations': po.invoice_ids.mapped(lambda invoice: {
                    'difference_amount': formatLang(self.env, invoice.amount_untaxed - po.amount_untaxed),
                    'comment': '',
                    'po_preparer': po.create_uid.name,
                    'po_validor': ', '.join(get_approval_entries(po.id, [
                        self.env.ref('choreograph_sox.group_validator_1_purchase_profile_res_groups').id,
                        self.env.ref('choreograph_sox.group_validator_2_purchase_profile_res_groups').id])),
                    'net_marging': formatLang(self.env, order_id.amount_untaxed - invoice.amount_untaxed)
                }),
            })
            datas['orders'].append({
                'name': order_id.name,
                'client': order_id.partner_id.name,
                'amount': formatLang(self.env, order_id.amount_untaxed),
                'delivery_date': format_datetime(self.env, order_id.commitment_date, dt_format=FORMAT_DATE),
                'purchase_data': po_list

            })
        return datas
