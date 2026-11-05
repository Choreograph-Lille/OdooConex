# -*- coding: utf-8 -*-

import paramiko
import logging
import io
import csv
import base64
from datetime import datetime, timedelta
import os

import pytz


_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare

AUTHORIZED_PAYMENT_STATE = ('En paiement', 'Extourné')

# Sage names its files with the French local date of generation.
SAGE_TZ = 'Europe/Paris'
# Number of days (before today) scanned on the SFTP to catch up missed files.
CATCHUP_DAYS_PARAM = 'choreograph_sage_sftp_import.catchup_days'
DEFAULT_CATCHUP_DAYS = 30


class AccountMove(models.Model):
    _inherit = 'account.move'

    # ------------------------------------------------------------------
    # File name management
    # ------------------------------------------------------------------

    def _get_sage_file_config(self):
        """Return (prefix, suffix, forced_date_str) for the move_type in context.

        Overridden by choreograph_sage_purchase_account / choreograph_sage_sale_account.
        """
        return False, False, False

    def _get_sage_today(self):
        """Today's date in the French timezone (independent of UTC / DST)."""
        return fields.Date.context_today(self.with_context(tz=SAGE_TZ))

    def _parse_sage_forced_date(self, value):
        """Convert the 'Date import' setting to a date.

        The purchase setting is a Datetime stored in UTC: convert it back to the
        French date, otherwise a date entered at midnight would shift to the day before.
        """
        if not value:
            return False
        if len(value) > 10:
            utc_dt = fields.Datetime.from_string(value)
            return pytz.utc.localize(utc_dt).astimezone(pytz.timezone(SAGE_TZ)).date()
        return fields.Date.from_string(value)

    def _build_sage_file_name(self, file_date):
        prefix, suffix, _forced_date = self._get_sage_file_config()
        file_name = f"{file_date.strftime('%Y%m%d')}.csv"
        if prefix:
            file_name = f"{prefix}_{file_name}"
        if suffix:
            file_name = f"{file_name}_{suffix}"
        return file_name

    def get_file_name(self):
        """Name of the file to import when a single file is targeted:
        the forced 'Date import' if set, otherwise the file of yesterday (French date)."""
        forced_date = self._parse_sage_forced_date(self._get_sage_file_config()[2])
        return self._build_sage_file_name(forced_date or self._get_sage_today() - timedelta(days=1))

    def _get_sage_catchup_days(self):
        value = self.env['ir.config_parameter'].sudo().get_param(CATCHUP_DAYS_PARAM)
        try:
            days = int(value)
        except (TypeError, ValueError):
            days = DEFAULT_CATCHUP_DAYS
        return max(days, 1)

    def _get_sage_files_to_import(self, ftp_server, list_dir, log_type):
        """Return the file names to import, oldest first.

        - 'Date import' set: only that file (manual relaunch, even if already imported).
        - Otherwise: every file of the last N days (today excluded, it may still be in
          transfer) present on the SFTP and never read yet, i.e. without an import log
          bearing its name.
        """
        forced_date = self._parse_sage_forced_date(self._get_sage_file_config()[2])
        if forced_date:
            return [self._build_sage_file_name(forced_date)]

        today = self._get_sage_today()
        candidates = [
            self._build_sage_file_name(today - timedelta(days=delta))
            for delta in range(self._get_sage_catchup_days(), 0, -1)
        ]
        present = [name for name in candidates if name in list_dir]
        if not present:
            return []
        already_read = set(self.env['sftp.import.report'].search([
            ('type', '=', log_type),
            ('file_name', 'in', present),
        ]).mapped('file_name'))
        return [name for name in present if name not in already_read]

    def is_present_file(self, filename, listdir):
        if filename in listdir:
            return True
        else:
            return False


    def get_sftp_client_import(self, ftp_server):
        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        passphrase = ftp_server.passphrase

        try:
            if ftp_server.key_attachment_id:
                # Get path of key as attachment
                key_path = ftp_server.key_attachment_id._full_path(
                    ftp_server.key_attachment_id.store_fname
                )
                key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
                ssh_client.connect(ftp_server.host, ftp_server.port, ftp_server.username, pkey=key)
            else:
                ssh_client.connect(
                    ftp_server.host,
                    int(ftp_server.port),
                    ftp_server.username,
                    password=passphrase,
                )
            return ssh_client

        except Exception as e:
            raise UserError(_('Could not etablish connexion to ftp server, reason %s') % e)

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

    def download_file(self, ftp_server, ssh_client, log, filename=None, sftp=None):
        """Read the CSV file `filename` (default: get_file_name()) and return its rows."""
        filename = filename or self.get_file_name()
        file_path = f"{ftp_server.output_path}/{filename}"
        sftp = sftp or ssh_client.open_sftp()

        # Try to read file first
        list_dir = sftp.listdir(f'/{ftp_server.output_path}')
        if not self.is_present_file(filename, list_dir):
            _logger.info('File %s not found' % filename)
            self._validation_error(
                log,
                _("File not found"),
                "file_not_found",
            )
            return []

        try:
            with sftp.open(file_path, "rb") as file:
                file_bytes = file.read()
                attachment = self.env["ir.attachment"].create({
                    "name": os.path.basename(file_path),
                    "datas": base64.b64encode(file_bytes),
                    "type": "binary",
                    "mimetype": "text/csv",
                })
                log.write({'attachment_id': attachment.id, 'file_name': attachment.name})

            csv_text = file_bytes.decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(csv_text), delimiter="\t")

            if not reader.fieldnames:
                self._validation_error(
                    log,
                    _("CSV file has no header."),
                    "file_invalid",
                )
                return []

            required_columns = {
                "Référence Pièce",
                "Statut paiement",
                "Siren tiers",
                "Montant payé",
                "Devise",
                "ID ODOO"
            }

            missing_columns = required_columns - set(reader.fieldnames)

            if missing_columns:
                self._validation_error(
                    log,
                    _("Missing required column(s): %s")
                    % ", ".join(sorted(missing_columns)),
                    "file_invalid",
                )
                return []

            rows = list(reader)
            return rows

        except FileNotFoundError:
            message = _("File not found: %s") % file_path
            error_type = "file_not_found"

        except UnicodeDecodeError:
            message = _("File is not a valid UTF-8 CSV.")
            error_type = "file_invalid"

        except csv.Error as exc:
            message = _("Invalid CSV file: %s") % exc
            error_type = "file_invalid"

        except OSError as exc:
            message = _("Unable to read file: %s") % exc
            error_type = "file_not_found"

        self.create_sftp_log_line(
            log=log,
            message=message,
            error_type=error_type,
        )
        return []

    def validate_data_import(self, invoice_data, log, move_type):
        """Validate a single invoice row from the import."""

        ref = invoice_data.get("Référence Pièce")

        if not ref:
            return self._validation_error(
                log,
                _("Invoice reference is missing."),
                "file_invalid",
            )
        odoo_id = invoice_data.get('ID ODOO')
        move = self.env['account.move']
        try:
            move_id = int(odoo_id)
            virtual_move = self.env["account.move"].browse(move_id)
            move = virtual_move if virtual_move.exists() else self.env['account.move']
        except Exception as e:
            _logger.error("Impossible to get move by ID odoo, reason: %s" % e)

        if not move:
            domain = [('move_type', '=', move_type)]
            if move_type == 'in_invoice':
                domain += [("ref", "=", ref)]
            else:
                domain += [('name', '=', ref)]
            move = self.env["account.move"].search(domain,limit=1)

        if not move:
            return self._validation_error(
                log,
                _("Account move with reference '%s' was not found.") % ref,
                "invoice_not_found",
                ref,
            )

        if move.state != "posted":
            return self._validation_error(
                log,
                _("Invoice must be posted."),
                "wrong_state",
                ref,
            )

        payment_state = invoice_data.get("Statut paiement")

        if payment_state not in AUTHORIZED_PAYMENT_STATE:
            return self._validation_error(
                log,
                _("Unknown payment state '%s'. Expected one of: %s.")
                % (payment_state, ", ".join(AUTHORIZED_PAYMENT_STATE)),
                "unknown_status",
                ref,
            )

        if move.amount_residual == 0:
            return self._validation_error(
                log,
                _("Invoice has already been paid."),
                "data_mismatch",
                ref,
            )

        siren = invoice_data.get("Siren tiers")

        if siren and move.siren != siren:
            return self._validation_error(
                log,
                _("Supplier SIREN does not match the invoice."),
                "data_mismatch",
                ref,
            )

        amount_str = invoice_data.get("Montant payé")

        try:
            amount = float(amount_str.replace(",", "."))
        except (AttributeError, ValueError):
            return self._validation_error(
                log,
                _("Invalid payment amount: '%s'.") % amount_str,
                "data_mismatch",
                ref,
            )

        currency = invoice_data.get('Devise') or ''
        if move.currency_id.name.strip().lower() != currency.strip().lower():
            return self._validation_error(
                log,
                _("Currency does not match"),
                "data_mismatch",
                ref,
            )

        # Check if the amount to pay is different of amount_total only if the currency is same as main company
        # Currency rounding: a total of 123.60000000000001 must match 123.60
        same_amount = float_compare(
            amount, move.amount_total, precision_rounding=move.currency_id.rounding) == 0
        if not same_amount and move.currency_id == move.company_id.currency_id:
            return self._validation_error(
                log,
                _("Payment amount does not match the invoice total."),
                "data_mismatch",
                ref,
            )

        return move

    def create_sftp_log(self, sftp_server_id,type,attachment=False):
        log = self.env['sftp.import.report'].create({
            'import_date': fields.Datetime.now(),
            'type': type,
            'attachment_id': attachment.id if attachment else False,
            'file_name': attachment.name if attachment else False,
            'sftp_server_id': sftp_server_id.id
        })
        return log

    def create_sftp_log_line(self, log, message, error_type, ref=False):
        self.env['sftp.import.report.line'].create({
            'report_id': log.id,
            'message': message,
            'invoice_ref': ref,
            'error_type': error_type
        })

    def get_payment_date(self, date_str):
        try:
            payment_date = datetime.strptime(date_str, '%d/%m/%Y').date()
            return payment_date
        except Exception as e:
            _logger.error('Could not convert %s to date, reason: %s' % (date_str, e))
            return fields.Date.today()

    def create_payment(self, payment_date=False):
        config_parameter = self.env['ir.config_parameter'].sudo()
        journal_id = config_parameter.get_param('choreograph_sage_purchase_account.purchase_default_journal_id', False)
        payment_vals = {
            'payment_date': self.get_payment_date(payment_date)
        }
        if journal_id:
            payment_vals.update({'journal_id': int(journal_id)})
        wizard = self.env['account.payment.register'].with_context(
            active_model='account.move',
            active_ids=self.ids,
        ).create(payment_vals)
        wizard._create_payments()
        _logger.info("Payment created successfully for account move %s" % self.id)
    
    def create_sale_payment(self,data):
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

    # ------------------------------------------------------------------
    # Import engine (shared by purchase and sale imports)
    # ------------------------------------------------------------------

    def _register_sage_payment(self, move, data, move_type):
        if move_type == 'in_invoice':
            move.create_payment(payment_date=data.get('Date paiement'))
        else:
            move.create_sale_payment(data)

    @api.model
    def _run_sage_import(self, move_type, log_type):
        """Import every Sage file not imported yet (see _get_sage_files_to_import)."""
        self = self.with_context(move_type=move_type)
        sftp_server_param = self.env['ir.config_parameter'].sudo().get_param(
            'choreograph_sage_sftp_import.sftp_server_id', False)
        sftp_server_id = self.env['choreograph.sage.sftp.server'].browse(
            int(sftp_server_param)) if sftp_server_param else False
        if not sftp_server_id:
            return False

        ssh_client = self.get_sftp_client_import(sftp_server_id)
        try:
            sftp = ssh_client.open_sftp()
            list_dir = sftp.listdir(f'/{sftp_server_id.output_path}')
            file_names = self._get_sage_files_to_import(sftp_server_id, list_dir, log_type)
            if not file_names:
                log = self.create_sftp_log(sftp_server_id, log_type)
                self._validation_error(
                    log,
                    _("No new file to import over the last %s days.") % self._get_sage_catchup_days(),
                    "file_not_found",
                )
                log.state = 'rejected'
                return False
            for file_name in file_names:
                self._import_sage_file(sftp_server_id, ssh_client, sftp, file_name, move_type, log_type)
        finally:
            ssh_client.close()
        return True

    def _import_sage_file(self, sftp_server_id, ssh_client, sftp, file_name, move_type, log_type):
        """Import one Sage file and fill its import log."""
        start = datetime.now()
        log = self.create_sftp_log(sftp_server_id, log_type)
        try:
            with self.env.cr.savepoint():
                self._process_sage_file(sftp_server_id, ssh_client, sftp, file_name, move_type, log)
        except Exception as e:
            _logger.exception("Unexpected error while importing Sage file %s", file_name)
            # Keep the file name on the log: the file is considered as read and won't be
            # retried every day; it can be relaunched manually with 'Date import'.
            log.write({'file_name': file_name, 'state': 'failed', 'message': str(e)})
        log.duration = (datetime.now() - start).seconds

    def _process_sage_file(self, sftp_server_id, ssh_client, sftp, file_name, move_type, log):
        datas = self.download_file(sftp_server_id, ssh_client, log, filename=file_name, sftp=sftp)
        if not datas:
            if log.error_line_ids:
                log.state = 'rejected'
            else:
                # Header only: Sage writes a file every day, even when there is no payment
                log.write({
                    'state': 'success',
                    'message': _("Empty file: no payment to import."),
                })
            return

        line_count = 0
        error_count = 0
        success_count = 0
        for data in datas:
            try:
                # Savepoint: a database error on one line must not break the whole import
                with self.env.cr.savepoint():
                    move_id = self.validate_data_import(data, log, move_type)
                    if move_id:
                        payment_state = data.get('Statut paiement')
                        if move_id.amount_residual > 0 and payment_state == 'En paiement':
                            self._register_sage_payment(move_id, data, move_type)
                            success_count += 1
                        else:
                            self.create_sftp_log_line(
                                log=log,
                                message=_("Invoice cannot be paid; please check the remaining balance or whether a reversal has already been created."),
                                error_type="data_mismatch",
                                ref=data.get("Référence Pièce"),
                            )
                            error_count += 1
                    else:
                        error_count += 1
            except Exception as e:
                _logger.exception(
                    "Unexpected error while processing line with reference '%s'",
                    data.get("Référence Pièce")
                )
                self.create_sftp_log_line(
                    log=log,
                    message=str(e),
                    error_type="file_invalid",
                    ref=data.get("Référence Pièce"),
                )
                error_count += 1
            finally:
                line_count += 1
        log.line_count = line_count
        log.error_count = error_count
        log.success_count = success_count
        if line_count == error_count:
            log.state = 'failed'
        elif line_count == success_count:
            log.state = 'success'
        else:
            log.state = 'partial'

