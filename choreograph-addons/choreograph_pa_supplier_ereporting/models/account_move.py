# -*- coding: utf-8 -*-

import csv
import io
import logging

from odoo import _, api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

EREPORTING_PF_CODES = ("B2C", "B2BINT")
EREPORTING_MOVE_TYPES = ("in_invoice", "in_refund")
EREPORTING_DEFAULT_PATH = "ereporting"
EREPORTING_TAX_SEPARATOR = " / "

# The file layout is set by the PA ICD: the header and the values are always in French
EREPORTING_HEADER = [
    "Numéro de la facture",
    "Date de facturation",
    "Date échéance",
    "Type",
    "Devise",
    "SIREN Vendeur",
    "SIREN Acheteur",
    "Montant HT",
    "Montant TVA",
    "Montant TTC",
    "Type TVA",
    "Code TVA",
    "VATEX",
]
EREPORTING_TYPE_LABELS = {
    "in_invoice": "Facture fournisseur",
    "in_refund": "Avoir fournisseur",
}


class AccountMove(models.Model):
    _inherit = "account.move"

    is_transferred_to_ereporting = fields.Boolean(
        string="E-Reporting Transfer",
        copy=False,
        readonly=True,
        help="Checked once the document has been sent to the PA ICD in the E-Reporting file.",
    )

    # ------------------------------------------------------------------
    # Selection
    # ------------------------------------------------------------------

    @api.model
    def _get_ereporting_vendors(self):
        """Vendors whose 'PF Code Identification' is B2C or B2BINT."""
        partners = self.env["res.partner"].with_context(active_test=False).search(
            [("pf_code_identification", "!=", False)])
        return partners.filtered(
            lambda p: p.pf_code_identification.strip().upper() in EREPORTING_PF_CODES)

    @api.model
    def _get_ereporting_domain(self):
        # The domain uses tuples on purpose: choreograph_sox hides confidential supplier
        # invoices only when the domain uses lists, and these invoices must be reported too
        return [
            ("move_type", "in", EREPORTING_MOVE_TYPES),
            ("state", "=", "posted"),
            ("is_transferred_to_ereporting", "=", False),
            ("commercial_partner_id", "in", self._get_ereporting_vendors().ids),
        ]

    # ------------------------------------------------------------------
    # File content
    # ------------------------------------------------------------------

    def _get_ereporting_taxes(self):
        self.ensure_one()
        lines = self.invoice_line_ids.filtered(lambda line: line.display_type == "product")
        return lines.tax_ids.sorted(lambda tax: (tax.sequence, tax.id))

    def _get_ereporting_missing_fields(self, taxes):
        """Every column is mandatory: return the label of each missing value."""
        self.ensure_one()
        missing = []
        if not self.ref:
            missing.append(_("invoice reference"))
        if not self.provider_invoice_date:
            missing.append(_("provider invoice date"))
        if not self.invoice_date_due:
            missing.append(_("due date"))
        if not self.siren:
            missing.append(_("vendor SIREN"))
        if not self.company_id.siren:
            missing.append(_("SIREN of the company %s") % self.company_id.name)
        if not taxes:
            missing.append(_("VAT (no tax on the invoice lines)"))
        else:
            no_category = taxes.filtered(lambda tax: not tax.unece_categ_code)
            if no_category:
                missing.append(_("UNECE tax category on %s") % ", ".join(no_category.mapped("name")))
        if not self.commercial_partner_id.vatex:
            missing.append(_("VATEX on the vendor %s") % self.commercial_partner_id.name)
        return missing

    def _prepare_ereporting_row(self):
        """Return (row, missing fields). The row is None when a value is missing."""
        self.ensure_one()
        taxes = self._get_ereporting_taxes()
        missing = self._get_ereporting_missing_fields(taxes)
        if missing:
            return None, missing
        # The file is in French whatever the language of the user running the export
        tax_names = taxes.with_context(lang="fr_FR").mapped("name")
        # Several different taxes: their names and codes are joined in the same column
        tax_codes = list(dict.fromkeys(taxes.mapped("unece_categ_code")))
        row = [
            self.ref,
            self.provider_invoice_date.strftime("%d/%m/%Y"),
            self.invoice_date_due.strftime("%d/%m/%Y"),
            EREPORTING_TYPE_LABELS[self.move_type],
            self.currency_id.name,
            self.siren,
            self.company_id.siren,
            "%.2f" % self.amount_untaxed,
            "%.2f" % self.amount_tax,
            "%.2f" % self.amount_total,
            EREPORTING_TAX_SEPARATOR.join(tax_names),
            EREPORTING_TAX_SEPARATOR.join(tax_codes),
            self.commercial_partner_id.vatex,
        ]
        return row, []

    @api.model
    def _build_ereporting_csv(self, rows):
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter="\t")
        writer.writerow(EREPORTING_HEADER)
        writer.writerows(rows)
        return buffer.getvalue().encode("utf-8")

    @api.model
    def _get_ereporting_today(self):
        # Date in Paris time: in UTC the cron could take the previous day (see HT11016)
        return fields.Datetime.context_timestamp(
            self.with_context(tz="Europe/Paris"), fields.Datetime.now()).date()

    @api.model
    def _get_ereporting_file_name(self):
        return "E-Reporting_Fournisseurs_%s.csv" % self._get_ereporting_today().strftime("%d%m%Y")

    # ------------------------------------------------------------------
    # SFTP
    # ------------------------------------------------------------------

    @api.model
    def _upload_ereporting_file(self, ftp_server, file_name, content):
        """Send the file and return its final name.

        A file already sent the same day is never overwritten: the new one gets
        a _2, _3... suffix, so the documents of the first file are not lost.
        """
        if not ftp_server:
            raise UserError(_("No SFTP server is configured for the PA ICD."))
        directory = (self.env["ir.config_parameter"].sudo().get_param(
            "choreograph_pa_supplier_ereporting.remote_path") or EREPORTING_DEFAULT_PATH).rstrip("/")
        ssh_client, sftp = self.get_sftp_client(ftp_server)
        try:
            base_name = file_name[:-len(".csv")]
            index = 1
            while True:
                try:
                    sftp.stat(f"{directory}/{file_name}")
                except FileNotFoundError:
                    break
                index += 1
                file_name = f"{base_name}_{index}.csv"
            with sftp.open(f"{directory}/{file_name}", "wb") as remote_file:
                remote_file.write(content)
        finally:
            sftp.close()
            ssh_client.close()
        return file_name

    # ------------------------------------------------------------------
    # Cron
    # ------------------------------------------------------------------

    @api.model
    def export_ereporting_supplier_to_pa(self):
        """Weekly cron: send the supplier invoices and credit notes to the PA ICD (E-Reporting)."""
        ftp_server = self._get_ftp_server("choreograph_sage_sale_account_export.sftp_ubl_server_id")
        file_name = self._get_ereporting_file_name()
        log_vals = {
            "type": "ereporting_supplier",
            "export_date": fields.Datetime.now(),
            "file_name": file_name,
            "sftp_server_id": ftp_server.id if ftp_server else False,
        }
        report_model = self.env["sftp.export.report"].sudo()

        moves = self.search(self._get_ereporting_domain(), order="name")
        if not moves:
            log_vals.update({
                "state": "success",
                "line_count": 0,
                "message": _("No supplier invoice or credit note to transfer."),
            })
            return report_model.create(log_vals)

        rows = []
        exported = self.browse()
        errors = []
        for move in moves:
            row, missing = move._prepare_ereporting_row()
            if missing:
                errors.append("%s : %s" % (move.name, ", ".join(missing)))
            else:
                rows.append(row)
                exported |= move
        log_vals.update({"line_count": len(moves), "error_count": len(errors)})
        error_message = ""
        if errors:
            error_message = "\n".join(
                [_("%s document(s) in error, not sent:") % len(errors)] + errors)

        if rows:
            content = self._build_ereporting_csv(rows)
            try:
                file_name = self._upload_ereporting_file(ftp_server, file_name, content)
            except Exception as error:
                _logger.exception("E-Reporting: the file could not be sent to the PA ICD")
                log_vals.update({
                    "state": "failed",
                    "success_count": 0,
                    "error_count": len(moves),
                    "message": "\n".join(filter(None, [
                        _("The file could not be sent to the SFTP server, so no document is "
                          "marked as transferred. Error: %s") % error,
                        error_message,
                    ])),
                })
                log_vals["attachment_id"] = self._create_ereporting_attachment(file_name, content).id
                return report_model.create(log_vals)
            log_vals["file_name"] = file_name
            log_vals["attachment_id"] = self._create_ereporting_attachment(file_name, content).id
            # One write per document: the account.move write of choreograph_sox
            # only accepts one record, and refunds need force_write
            comment = _("Sent on %(date)s in the file %(file)s") % {
                "date": self._get_ereporting_today().strftime("%d/%m/%Y"),
                "file": file_name,
            }
            for move in exported:
                move.with_context(force_write=True).write({"is_transferred_to_ereporting": True})
                # Internal note: followers are not notified
                move.message_post(body=_("E-Reporting: %s") % comment, subtype_xmlid="mail.mt_note")

        if not errors:
            state = "success"
        elif not exported:
            state = "failed"
        else:
            state = "partial"
        log_vals.update({
            "state": state,
            "success_count": len(exported),
            "exported_move_names": ", ".join(exported.mapped("name")) or False,
            "message": "\n".join(filter(None, [
                _("%s document(s) sent to the PA ICD.") % len(exported) if exported else "",
                error_message,
            ])),
        })
        if not rows:
            log_vals["file_name"] = False
        _logger.info("E-Reporting: %s document(s) sent, %s in error", len(exported), len(errors))
        return report_model.create(log_vals)

    @api.model
    def _create_ereporting_attachment(self, file_name, content):
        return self.env["ir.attachment"].sudo().create({
            "name": file_name,
            "raw": content,
            "mimetype": "text/csv",
        })
