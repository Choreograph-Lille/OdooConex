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
        passphrase = ftp_server.passphrase

        try:
            if ftp_server.key_attachment_id:
                key_path = ftp_server.key_attachment_id._full_path(
                            ftp_server.key_attachment_id.store_fname
                        )
                key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
                ssh_client.connect(
                    ftp_server.host, int(ftp_server.port), ftp_server.username, pkey=key
                )
            else:
                ssh_client.connect(
                    ftp_server.host, 
                    int(ftp_server.port), 
                    ftp_server.username, 
                    password=ftp_server.passphrase
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
