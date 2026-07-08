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

    def download_file(self,log, ftp_server=False,):
        # file_path = f"{ftp_server.full_path}/{self.get_file_name()}"
        file_path = self.env['ir.config_parameter'].sudo().get_param('choreograph_sage_purchase_account.sage_test_ftp_directory')
        try:
            with open(file_path, mode="rb") as f:
                file_bytes = f.read()
                # Convert file to dict
                csv_text = file_bytes.decode("utf-8")
                reader = csv.DictReader(io.StringIO(csv_text), delimiter="\t")

                if reader.fieldnames is None:
                    self.create_sftp_log_line(
                        log=log,
                        message="CSV file has no header",
                        error_type='file_invalid',
                    )
                    return False, []

                rows = list(reader)
                # Save content as attachment
                attachment = self.env['ir.attachment'].create({
                    "name": os.path.basename(file_path),
                    "datas": base64.b64encode(file_bytes),
                    'type': 'binary',
                    "mimetype": "text/csv",
                })
                return attachment, rows

        except UnicodeDecodeError:
            error = "File is not a valid UTF-8 CSV"
            self.create_sftp_log_line(
                log=log,
                message=error,
                error_type='file_invalid'
            )
            return False, []

        except csv.Error as csv_error:
            self.create_sftp_log_line(
                log=log,
                message='Csv invalid: %s' % csv_error,
                error_type='file_invalid'
            )
            return False, []
        except Exception as e:
            self.create_sftp_log_line(
                log=log,
                message='Cannot import file, reason: %s' % e,
                error_type='file_not_found'
            )
            return False, []



    def validate_data_import(self, invoice_data, log):
        ref = invoice_data.get('Référence Pièce')
        if not ref:
            error = 'Invoice reference is not present in header'
            _logger.info(error)
            self.create_sftp_log_line(
                log=log,
                message=error,
                error_type='file_invalid'
            )
            return False

        move_id = self.env['account.move'].search([('ref', '=', ref)], limit=1)
        if not move_id:
            error = 'Account move with ref %s not found' % ref
            _logger.info(error)
            self.create_sftp_log_line(
                log=log,
                message=error,
                error_type='invoice_not_found',
                ref=ref
            )
            return False

        if move_id.state != 'posted':
            error = 'Invoice should be not in draft or cancel state'
            _logger.info(error)
            self.create_sftp_log_line(
                log=log,
                message=error,
                error_type='wrong_state',
                ref=ref
            )
            return False

        if invoice_data.get('Statut de paiement') not in AUTHORIZED_PAYMENT_STATE:
            error = 'Value of payment state should be among %s' % ','.join(AUTHORIZED_PAYMENT_STATE)
            _logger.error(error)
            self.create_sftp_log_line(
                log=log,
                message=error,
                error_type='unkown_status',
                ref=ref
            )
            return False

        if move_id.amount_residual == 0:
            error = 'The invoice has already been paid'
            _logger.info(error)
            self.create_sftp_log_line(
                log=log,
                message=error,
                error_type='data_mismatch',
                ref=ref
            )
            return False

        siren = invoice_data.get('SIREN du fournisseur')
        if not siren:
            error = 'Siren not found'
            self.create_sftp_log_line(
                log=log,
                message=error,
                error_type='data_mismatch',
                ref=ref
            )
            return False

        if move_id.siren != siren:
            error = "The supplier's SIREN number does not match"
            self.create_sftp_log_line(
                log=log,
                message=error,
                error_type='data_mismatch',
                ref=ref
            )
            _logger.info(error)
            return False

        total_amount = float(invoice_data.get('Montant payé').replace(',', '.'))
        if total_amount != move_id.amount_total:
            error = 'The given amount total does not correspond to the actual amount'
            self.create_sftp_log_line(
                log=log,
                message=error,
                error_type='data_mismatch',
                ref=ref
            )
            _logger.info(error)
            return False

        return move_id

    def create_sftp_log(self,sftp_server_id, attachment=False):
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
                    move_id = self.validate_data_import(data, log)
                    if move_id:
                        success_count += 1
                        self.create_payment(move_id, data)
                    else:
                        error_count += 1
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
