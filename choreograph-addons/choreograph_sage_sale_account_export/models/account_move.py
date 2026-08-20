# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
import csv
import io
from datetime import datetime, date
import paramiko
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    is_invoice_collected = fields.Boolean(copy=False)
    is_transferred_to_pa = fields.Boolean(string="Is transferred to PA ?",copy=False)

    def get_export_file_name(self):
        """Generate file name with date in DDMMYYYY format"""
        prefix = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("choreograph_sage_sale_account_export.prefix")
            or "EXPORTED_INVOICES"
        )
        suffix = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("choreograph_sage_sale_account_export.suffix")
            or ""
        )

        today = date.today().strftime("%d%m%Y")
        file_name = f"{prefix}_{today}.csv"
        if suffix:
            file_name = f"{prefix}_{today}_{suffix}.csv"
        return file_name

    def get_sftp_client(self, ftp_server):
        """Establish SFTP connection and return client"""
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        key_path = ftp_server.key_attachment_id._full_path(
            ftp_server.key_attachment_id.store_fname
        )
        passphrase = ftp_server.passphrase

        try:
            key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
            ssh_client.connect(
                ftp_server.host, int(ftp_server.port), ftp_server.username, pkey=key
            )

            sftp = ssh_client.open_sftp()
            return ssh_client, sftp

        except Exception as e:
            ssh_client.close()
            raise UserError(
                _("Could not establish connection to SFTP server, reason: %s") % e
            )

    def generate_paid_invoices_file(self):
        """Generate and export paid invoices to PA ICD via SFTP"""
        sftp_server_id = self.env['ir.config_parameter'].sudo().get_param(
            'choreograph_sage_sale_account_export.sftp_server_id')
        
        if not sftp_server_id:
            _logger.warning(_("Make sure to configure an SFTP server in settings!"))

        try:
            ftp_server = self.env["choreograph.sage.sftp.server"].browse(int(sftp_server_id))
            if not ftp_server.exists():
                _logger.warning(_("Configured SFTP server does not exist!"))
        except (ValueError, TypeError):
            _logger.warning(_("Invalid SFTP server configuration!"))

        today = date.today()

        moves = self.env["account.move"].search(
            [
                ("move_type", "in", ["out_invoice", "out_refund"]),
                ("state", "=", "posted"),
                ("payment_state", "=", "in_payment"),
                ("is_invoice_collected", "=", False),
            ]
        )

        if moves:
            self.create_paid_invoices_file(moves, ftp_server)

        return True

    def prepare_paid_invoices_rows(self, moves):
        """Prepare rows for the paid invoices CSV file"""
        invoice_number_label = _("Invoice Number")
        amount_ttc_label = _("Amount TTC")
        status_label = _("Status")

        fields_list = [invoice_number_label, amount_ttc_label, status_label]
        rows = []

        for move in moves:
            if move.move_type in ["out_invoice", "out_refund"]:
                vals = {
                    invoice_number_label: move.name,
                    amount_ttc_label: abs(move.amount_total),
                    status_label: _("Collected"),
                }
                rows.append(vals)

        return fields_list, rows

    def create_paid_invoices_file(self, moves, ftp_server):
        """Create the paid invoices CSV file and upload to SFTP"""
        ssh_client = None
        sftp = None
        file_name = None
        upload_successful = False
        message = None
        state = None

        try:
            fields_list, rows = self.prepare_paid_invoices_rows(moves)

            file_name = self.get_export_file_name()
            temp_file = f"/tmp/{file_name}"

            with open(temp_file, "w", newline="", encoding="utf-8") as temp:
                writer = csv.DictWriter(temp, delimiter="\t", fieldnames=fields_list)
                writer.writeheader()
                writer.writerows(rows)

            try:
                if ftp_server :
                    ssh_client, sftp = self.get_sftp_client(ftp_server)
                    sftp.put(temp_file, f"{ftp_server.output_path}/{file_name}")
                    upload_successful = True
                    state = "success"
                    message = _("File uploaded successfully")
                else:
                    raise UserError(_("No SFTP server configured for export!"))
            except Exception as ftp_error:
                state = "failed"
                message = _("FTP upload error: %s") % str(ftp_error)
                _logger.warning(_("Paid invoices export FTP error: %s") % str(ftp_error))

            with open(temp_file, "rb") as file:
                file_content = base64.b64encode(file.read())

                self.create_export_log(
                    state,
                    "invoice_collected",
                    file_content,
                    file_name,
                    len(moves),
                    message,
                    ftp_server,
                    moves,
                )

            if upload_successful:
                for move in moves:
                    move.write({"is_invoice_collected": True})

                _logger.info(
                    _("Paid invoices export: %s invoices exported to %s") % (len(moves), file_name)
                )

        except Exception as e:
            state = "failed"
            message = str(e)
            self.create_export_log(
                state,
                "invoice_collected",
                None,
                file_name or self.get_export_file_name(),
                0,
                message,
                ftp_server,
                None,
            )
            _logger.error(_("Paid invoices export failed: %s") % (str(e) if ftp_server else _("No SFTP server configured")))

        finally:
            if sftp:
                sftp.close()
            if ssh_client:
                ssh_client.close()

        return True

    def create_export_log(
        self,
        state,
        export_type,
        file=None,
        file_name=None,
        line_count=None,
        message=None,
        ftp_server=None,
        moves=None,
    ):
        """Create export log with details"""
        log_vals = {
            "export_date": datetime.now(),
            "file_name": file_name,
            "type": export_type,
            "line_count": line_count,
            "message": message,
            "state": state,
            "sftp_server_id": ftp_server.id if ftp_server else None,
        }

        if file:
            attachment_vals = {
                "datas": file,
                "name": file_name,
            }
            attachment_id = self.env["ir.attachment"].create(attachment_vals)
            log_vals["attachment_id"] = attachment_id.id

        report = self.env["sftp.export.report"].create(log_vals)

        if moves and state == "success":
            for move in moves:
                line_vals = {
                    "report_id": report.id,
                    "invoice_ref": move.name,
                    "amount_total": move.amount_total,
                    "status": _("Collected"),
                }
                self.env["sftp.export.report.line"].create(line_vals)

        return report
    
    def get_ubl_filename(self, version="2.1"):
        """
        Format :
          Facture : FAC-2026-00331_29062026.xml
          Avoir   : RFAC-2026-00003_29062026.xml
        """
        today = date.today().strftime('%d%m%Y')
        ref = self.name.replace('/', '-')
        return f"{ref}_{today}.xml"

    def _get_ubl_content(self):
        """
        Generate UBL XML content for the invoice. 
        This method can be overridden in other modules to customize the UBL generation.
        """
        self.ensure_one()
        return self.generate_ubl_xml_string(version='2.1')

    def _get_export_type(self):
        """Return the export type based on the move type."""
        if self.move_type == 'out_invoice':
            return 'invoice'
        elif self.move_type == 'out_refund':
            return 'credit_note'
        return 'invoice'
    
    def _get_ftp_server(self, param_key):
        """
        Helper method to retrieve the SFTP server configuration based on a parameter key.
        """
        sftp_server_id = self.env['ir.config_parameter'].sudo().get_param(param_key)
        if not sftp_server_id:
            return None
        try:
            server = self.env['choreograph.sage.sftp.server'].browse(
                int(sftp_server_id))
            return server if server.exists() else None
        except (ValueError, TypeError):
            return None
    @api.model
    def export_ubl_invoices_to_pa(self):
        """
        Cron job method to export UBL invoices and credit notes to the PA ICD via SFTP.
        It retrieves the SFTP server configuration, searches for posted invoices and credit notes
        """
        ftp_server = self._get_ftp_server(
            'choreograph_sage_sale_account_export.sftp_ubl_server_id')

        if not ftp_server:
            _logger.warning('UBL export: no SFTP ICD server configured.')
            return False

        moves = self.env['account.move'].search([
            ('move_type', 'in', ['out_invoice', 'out_refund']),
            ('state', '=', 'posted'),
            ('is_transferred_to_pa', '=', False),
        ])

        if not moves:
            _logger.info('UBL export: no invoice or credit note to export.')
            return True

        ssh_client, sftp = self.get_sftp_client(ftp_server)

        report = self.env['sftp.export.report'].create({
            'export_date':    fields.Datetime.now(),
            'sftp_server_id': ftp_server.id,
            'file_name':      f"UBL_export_{date.today().strftime('%d%m%Y')}",
        })

        line_count = success_count = error_count = 0

        try:
            for move in moves:
                line_count += 1
                filename = move.get_ubl_filename()

                try:
                    ubl_content = move._get_ubl_content()

                    remote_path = f"{ftp_server.output_path}/{filename}"
                    with sftp.open(remote_path, 'wb') as remote_file:
                        remote_file.write(ubl_content)

                    move.write({'is_transferred_to_pa': True})

                    self.env['sftp.export.report.line'].create({
                        'report_id':    report.id,
                        'invoice_ref':  move.name,
                        'amount_total': move.amount_total,
                        'status':       _('Transferred'),
                        'type':         move._get_export_type(),
                    })
                    success_count += 1
                    _logger.info('UBL export: %s → %s', move.name, remote_path)

                except Exception as e:
                    error_count += 1
                    self.env['sftp.export.report.line'].create({
                        'report_id':    report.id,
                        'invoice_ref':  move.name,
                        'amount_total': move.amount_total,
                        'status':       _('Failed'),
                        'type':         move._get_export_type(),
                        'message':      str(e),
                    })
                    _logger.error('UBL export: error on %s — %s', move.name, e)

        finally:
            sftp.close()
            ssh_client.close()

            if error_count == 0:
                state = 'success'
            elif success_count == 0:
                state = 'failed'
            else:
                state = 'partial'

            report.write({
                'line_count':    line_count,
                'success_count': success_count,
                'error_count':   error_count,
                'state':         state,
            })

        return True
