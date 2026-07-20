# -*- coding: utf-8 -*-

import paramiko
import logging
import io
import csv
import base64
from datetime import datetime

_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _
from odoo.exceptions import UserError

AUTHORIZED_PAYMENT_STATE = ('En paiement', 'Extourné')


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_file_name(self):
        config_parameter = self.env['ir.config_parameter'].sudo()
        prefix = config_parameter.get_param(
            'choreograph_sage_sale_account.prefix') or False
        suffix = config_parameter.get_param(
            'choreograph_sage_sale_account.suffix') or False
        sage_date_str = config_parameter.get_param(
            'choreograph_sage_sale_account.sage_file_date') or False
        sage_date = (fields.Date.from_string(sage_date_str)
                     if sage_date_str else fields.Date.today())

        file_name = f"{sage_date.strftime('%Y%m%d')}.csv"
        if prefix:
            file_name = f"{prefix}_{file_name}"
        if suffix:
            file_name = f"{file_name}_{suffix}"
        return file_name


    def is_present_file(self, filename, listdir):
        if filename in listdir:
            return True
        else:
            return False

    def get_sftp_client(self, ftp_server):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_path = ftp_server.key_attachment_id._full_path(
            ftp_server.key_attachment_id.store_fname)
        passphrase = ftp_server.passphrase
        try:
            key = paramiko.RSAKey.from_private_key_file(
                key_path, password=passphrase)
            ssh_client.connect(
                ftp_server.host, ftp_server.port,
                ftp_server.username, pkey=key)
            return ssh_client
        except Exception as e:
            raise UserError(
                _('Could not establish connection to SFTP server, reason: %s') % e)

    def _validation_error(self, log, message, error_type, ref=False):
        """Create a log line for a validation error and return False."""
        _logger.info(message)
        self.create_sftp_log_line(
            log=log,
            message=message,
            error_type=error_type,
            ref=ref,
        )
        return False

    def download_file(self, ftp_server, ssh_client, log):
        """Read the configured CSV file from SFTP and return its rows."""
        sftp = ssh_client.open_sftp()
        filename = self.get_file_name()
        file_path = f"{ftp_server.output_path}/{filename}"

        list_dir = sftp.listdir(ftp_server.output_path)
        if not self.is_present_file(filename, list_dir):
            _logger.info('File %s not found' % filename)
            self._validation_error(
                log,
                _('File %s not found on SFTP server.') % filename,
                'file_not_found',
            )
            return []

        try:
            with sftp.open(file_path, 'rb') as f:
                file_bytes = f.read()

            attachment = self.env['ir.attachment'].create({
                'name':     filename,
                'datas':    base64.b64encode(file_bytes),
                'type':     'binary',
                'mimetype': 'text/csv',
            })
            log.write({'attachment_id': attachment.id, 'file_name': attachment.name})

            csv_text = file_bytes.decode('utf-8-sig')
            reader = csv.DictReader(io.StringIO(csv_text), delimiter='\t')

            if not reader.fieldnames:
                self._validation_error(
                    log,
                    _('CSV file has no header.'),
                    'file_invalid',
                )
                return []

            required_columns = {
                'Référence Pièce',
                'Siren tiers',
                'Statut paiement',
                'Date paiement',
                'Montant payé',
                'Montant restant dû',
                'Devise',
                'ID ODOO',
            }
            missing_columns = required_columns - set(reader.fieldnames)
            if missing_columns:
                self._validation_error(
                    log,
                    _('Missing required column(s): %s') % ', '.join(
                        sorted(missing_columns)),
                    'file_invalid',
                )
                return []

            return list(reader)

        except UnicodeDecodeError:
            self._validation_error(
                log, _('File is not a valid UTF-8 CSV.'), 'file_invalid')
            return []

        except csv.Error as exc:
            self._validation_error(
                log, _('Invalid CSV file: %s') % exc, 'file_invalid')
            return []

        except Exception as exc:
            self._validation_error(
                log, _('Unable to read file: %s') % exc, 'file_not_found')
            return []

        finally:
            sftp.close()


    def validate_data_import(self, invoice_data, log):
        """Validate a single invoice row from the import."""
        ref     = (invoice_data.get('Référence Pièce') or '').strip()
        odoo_id = (invoice_data.get('ID ODOO') or '').strip()

        if not ref:
            return self._validation_error(
                log,
                _('Invoice reference is missing.'),
                'invoice_not_found',
            )

        move_id = None
        if odoo_id and odoo_id.isdigit():
            move_id = self.env['account.move'].browse(int(odoo_id))
            if not move_id.exists() or move_id.move_type != 'out_invoice':
                move_id = None

        if not move_id:
            move_id = self.env['account.move'].search([
                ('name', '=', ref),
                ('move_type', '=', 'out_invoice'),
            ], limit=1)

        if not move_id:
            return self._validation_error(
                log,
                _("Account move with reference '%s' was not found.") % ref,
                'invoice_not_found',
                ref,
            )

        if move_id.state != 'posted':
            return self._validation_error(
                log,
                _('Invoice %s must be posted.') % ref,
                'wrong_state',
                ref,
            )

        payment_state = (invoice_data.get('Statut paiement') or '').strip()
        if payment_state not in AUTHORIZED_PAYMENT_STATE:
            return self._validation_error(
                log,
                _("Unknown payment state '%s'. Expected one of: %s.") % (
                    payment_state, ', '.join(AUTHORIZED_PAYMENT_STATE)),
                'unknown_status',
                ref,
            )

        if move_id.amount_residual == 0:
            return self._validation_error(
                log,
                _('Invoice %s has already been paid.') % ref,
                'already_paid',
                ref,
            )

        siren = (invoice_data.get('Siren tiers') or '').strip()
        if siren and move_id.siren != siren:
            return self._validation_error(
                log,
                _("Customer SIREN does not match for invoice %s.") % ref,
                'data_mismatch',
                ref,
            )

        amount_str = (invoice_data.get('Montant payé') or '').strip()
        try:
            amount = float(amount_str.replace(',', '.'))
        except (AttributeError, ValueError):
            return self._validation_error(
                log,
                _("Invalid payment amount: '%s'.") % amount_str,
                'data_mismatch',
                ref,
            )

        if amount != move_id.amount_total:
            return self._validation_error(
                log,
                _('Payment amount does not match invoice total for %s: '
                  'Sage=%s, Odoo=%s.') % (ref, amount, move_id.amount_total),
                'data_mismatch',
                ref,
            )

        devise = (invoice_data.get('Devise') or '').strip()
        if devise and devise.lower() != move_id.currency_id.name.strip().lower():
            return self._validation_error(
                log,
                _('Currency mismatch for invoice %s: Sage=%s, Odoo=%s.') % (
                    ref, devise, move_id.currency_id.name),
                'data_mismatch',
                ref,
            )

        return move_id

    def create_sftp_log(self, sftp_server_id, attachment=False):
        return self.env['sftp.import.report'].create({
            'import_date':    fields.Datetime.now(),
            'type':           'sale',
            'attachment_id':  attachment.id if attachment else False,
            'file_name':      attachment.name if attachment else False,
            'sftp_server_id': sftp_server_id.id,
        })

    def create_sftp_log_line(self, log, message, error_type, ref=False):
        self.env['sftp.import.report.line'].create({
            'report_id':   log.id,
            'message':     message,
            'invoice_ref': ref,
            'error_type':  error_type,
        })

    def create_payment(self,data):
        date_str = data.get('Date paiement' or '').strip()
        payment_date = datetime.strptime(date_str, '%d/%m/%Y').date() if date_str else fields.Date.today()
        amount = data.get('Montant payé' or '').strip()
        vals = {
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'partner_id':   self.partner_id.id,
            'amount':       amount,
            'currency_id':  self.currency_id.id,
            'payment_date' : payment_date,
        }
        wizard = self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=self.ids,
        ).create(vals)
        wizard._create_payments()
        _logger.info('Payment created successfully for account move %s', self.id)

    @api.model
    def import_account_move_out_invoice(self):
        sftp_server_id = self.env['choreograph.sage.sftp.server'].search(
            [('active', '=', True)], limit=1)

        if not sftp_server_id:
            _logger.warning('Sage sale import: no active SFTP server found.')
            return False

        ssh_client = self.get_sftp_client(sftp_server_id)
        start = datetime.now()
        log = self.create_sftp_log(sftp_server_id)

        datas = self.download_file(sftp_server_id, ssh_client, log)
        if not datas:
            log.state = 'rejected'
            ssh_client.close()
            return False

        line_count = error_count = success_count = 0
        processed_refs = set()

        try:
            for data in datas:
                try:
                    ref = (data.get('Référence Pièce') or '').strip()

                    if ref and ref in processed_refs:
                        error_count += 1
                        self.create_sftp_log_line(
                            log=log,
                            message=_('Duplicate reference %s in file, '
                                      'line skipped.') % ref,
                            error_type='data_mismatch',
                            ref=ref,
                        )
                        continue

                    move_id = self.validate_data_import(data, log)

                    if move_id:
                        payment_state = (
                            data.get('Statut paiement') or '').strip()

                        if payment_state == 'En paiement':
                            move_id.create_payment(data=data)
                            processed_refs.add(ref)
                            success_count += 1

                        elif payment_state == 'Extourné':
                            self.create_sftp_log_line(
                                log=log,
                                message=_(
                                    'Invoice %s has reversed status in Sage, '
                                    'no action taken. Please handle manually.'
                                ) % ref,
                                error_type='reversed',
                                ref=ref,
                            )
                            error_count += 1
                    else:
                        error_count += 1

                except Exception as e:
                    _logger.exception(
                        "Unexpected error while processing line '%s'",
                        data.get('Référence Pièce'),
                    )
                    self.create_sftp_log_line(
                        log=log,
                        message=str(e),
                        error_type='file_invalid',
                        ref=data.get('Référence Pièce'),
                    )
                    error_count += 1

                finally:
                    line_count += 1

            log.line_count    = line_count
            log.error_count   = error_count
            log.success_count = success_count

            if line_count == error_count:
                log.state = 'failed'
            elif line_count == success_count:
                log.state = 'success'
            else:
                log.state = 'partial'

        finally:
            end = datetime.now()
            log.duration = (end - start).seconds
            ssh_client.close()

        return True