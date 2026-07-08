# -*- coding: utf-8 -*-

import paramiko
import logging
import io
import csv
import base64
from datetime import datetime
import os


_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _
from odoo.exceptions import UserError

AUTHORIZED_PAYMENT_STATE = ('En paiement', 'Extourné')


class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_file_name(self):
        prefix = self.env['ir.config_parameter'].sudo().get_param('choreograph_sage_purchase_account.prefix') or False
        suffix = self.env['ir.config_parameter'].sudo().get_param('choreograph_sage_purchase_account.suffix') or False

        file_name = f"{fields.Date.today().strftime('%Y%m%d')}.csv"
        if prefix:
            file_name = prefix + file_name
        if suffix:
            file_name += suffix
        return file_name

    def is_present_file(self, filename, listdir):
        if filename in listdir:
            return True
        else:
            return False


    def get_sftp_client(self, ftp_server):
        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Get path of key as attachment
        key_path = ftp_server.key_attachment_id._full_path(ftp_server.key_attachment_id.store_fname)
        passphrase = ftp_server.passphrase

        try:
            key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
            ssh_client.connect(ftp_server.host, ftp_server.port, ftp_server.username, pkey=key)
            with paramiko.SFTPClient.from_transport(ssh_client.get_transport()) as sftp:
                list_dir = sftp.listdir(f'/{ftp_server.output_path}')
                filename = self.get_file_name()
                if self.is_present_file(filename, list_dir):
                    _logger.info('File %s found' % filename)
                    return sftp
                else:
                    _logger.info('File not found')
                    return False
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

    def download_file(self, log):
        """Read the configured CSV file and return its attachment and rows."""

        file_path = self.env["ir.config_parameter"].sudo().get_param(
            "choreograph_sage_purchase_account.sage_test_ftp_directory"
        )

        try:
            with open(file_path, "rb") as file:
                file_bytes = file.read()

            csv_text = file_bytes.decode("utf-8")
            reader = csv.DictReader(io.StringIO(csv_text), delimiter="\t")

            if not reader.fieldnames:
                return self._validation_error(
                    log,
                    "CSV file has no header.",
                    "file_invalid",
                ), []

            required_columns = {
                "Référence Pièce",
                "Statut de paiement",
                "SIREN du fournisseur",
                "Montant payé",
                "Devise"
            }

            missing_columns = required_columns - set(reader.fieldnames)

            if missing_columns:
                return self._validation_error(
                    log,
                    "Missing required column(s): %s"
                    % ", ".join(sorted(missing_columns)),
                    "file_invalid",
                ), []

            rows = list(reader)

            attachment = self.env["ir.attachment"].create({
                "name": os.path.basename(file_path),
                "datas": base64.b64encode(file_bytes),
                "type": "binary",
                "mimetype": "text/csv",
            })

            return attachment, rows

        except FileNotFoundError:
            message = f"File not found: {file_path}"
            error_type = "file_not_found"

        except UnicodeDecodeError:
            message = "File is not a valid UTF-8 CSV."
            error_type = "file_invalid"

        except csv.Error as exc:
            message = f"Invalid CSV file: {exc}"
            error_type = "file_invalid"

        except OSError as exc:
            message = f"Unable to read file: {exc}"
            error_type = "file_not_found"

        self.create_sftp_log_line(
            log=log,
            message=message,
            error_type=error_type,
        )
        return False, []

    def validate_data_import(self, invoice_data, log):
        """Validate a single invoice row from the import."""

        ref = invoice_data.get("Référence Pièce")

        if not ref:
            return self._validation_error(
                log,
                "Invoice reference is missing.",
                "file_invalid",
            )

        move = self.env["account.move"].search(
            [("ref", "=", ref)],
            limit=1,
        )

        if not move:
            return self._validation_error(
                log,
                f"Account move with reference '{ref}' was not found.",
                "invoice_not_found",
                ref,
            )


        if move.state != "posted":
            return self._validation_error(
                log,
                "Invoice must be posted.",
                "wrong_state",
                ref,
            )

        payment_state = invoice_data.get("Statut de paiement")

        if payment_state not in AUTHORIZED_PAYMENT_STATE:
            return self._validation_error(
                log,
                "Unknown payment state '%s'. Expected one of: %s."
                % (payment_state, ", ".join(AUTHORIZED_PAYMENT_STATE)),
                "unknown_status",
                ref,
            )

        if move.amount_residual == 0:
            return self._validation_error(
                log,
                "Invoice has already been paid.",
                "data_mismatch",
                ref,
            )

        siren = invoice_data.get("SIREN du fournisseur")

        if move.siren != siren:
            return self._validation_error(
                log,
                "Supplier SIREN does not match the invoice.",
                "data_mismatch",
                ref,
            )

        amount_str = invoice_data.get("Montant payé")

        try:
            amount = float(amount_str.replace(",", "."))
        except (AttributeError, ValueError):
            return self._validation_error(
                log,
                f"Invalid payment amount: '{amount_str}'.",
                "data_mismatch",
                ref,
            )

        currency = invoice_data.get('Devise') or ''
        if move.currency_id.name.strip().lower() != currency.strip().lower():
            return self._validation_error(
                log,
                "Currency does not match",
                "data_mismatch",
                ref,
            )

        if amount != move.amount_total:
            return self._validation_error(
                log,
                "Payment amount does not match the invoice total.",
                "data_mismatch",
                ref,
            )

        return move

    def create_sftp_log(self, sftp_server_id, attachment=False):
        log = self.env['sftp.import.report'].create({
            'import_date': fields.Datetime.now(),
            'type': 'purchase',
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

    def create_payment(self, move_id, data):
        payment_state = data.get('Statut de paiement')
        if move_id.amount_residual > 0 and payment_state == 'En paiement':
            wizard = self.env['account.payment.register'].with_context(
                active_model='account.move',
                active_ids=move_id.ids,
            ).create({})
            wizard._create_payments()


    @api.model
    def import_account_move_in_invoice(self):
        sftp_server_id = self.env['choreograph.sage.sftp.server'].search([('active', '=', True)], limit=1)
        if sftp_server_id:
            # sftp = self.get_sftp_client(sftp_server_id)
            start = datetime.now()
            log = self.create_sftp_log(sftp_server_id)
            attachment, datas = self.download_file(log)
            if attachment:
                log.write({'attachment_id': attachment.id, 'file_name': attachment.name})

                line_count = 0
                error_count = 0
                success_count = 0
                for data in datas:
                    try:
                        move_id = self.validate_data_import(data, log)
                        if move_id:
                            success_count += 1
                            self.create_payment(move_id, data)
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
                elif error_count != line_count and error_count != 0 and line_count != 0:
                    log.state = 'partial'
                end = datetime.now()
                log.duration = (end - start).seconds
