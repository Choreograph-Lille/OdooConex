# -*- coding: utf-8 -*-

import csv
import io
from unittest.mock import patch

from freezegun import freeze_time

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.choreograph_pa_supplier_ereporting.hooks import fill_provider_invoice_date, post_init_hook
# get_sftp_client is defined by the existing PA export module
from odoo.addons.choreograph_sage_sale_account_export.models.account_move import AccountMove
from odoo.tests import tagged


class FakeRemoteFile(io.BytesIO):
    def __init__(self, sftp, path):
        super().__init__()
        self.sftp = sftp
        self.path = path

    def close(self):
        self.sftp.files[self.path] = self.getvalue()
        super().close()


class FakeSFTP:
    def __init__(self, files=None, fail=False):
        self.files = dict(files or {})
        self.fail = fail

    def stat(self, path):
        if path not in self.files:
            raise FileNotFoundError(path)

    def open(self, path, mode="rb"):
        if self.fail:
            raise OSError("Permission denied")
        return FakeRemoteFile(self, path)

    def close(self):
        pass


class FakeSSH:
    def close(self):
        pass


@tagged("post_install", "-at_install")
class TestEReporting(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref="l10n_fr.l10n_fr_pcg_chart_template"):
        # French chart: l10n_generic_coa is not installed on Choreograph databases
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.pay_terms_a.sudo().company_id = False
        cls.env.user.groups_id |= cls.env.ref(
            "choreograph_sox.group_credit_note_preparer_profile_res_groups")
        cls.company_data["company"].siren = "489496331"

        cls.server = cls.env["choreograph.sage.sftp.server"].create({
            "name": "PA ICD test",
            "host": "localhost",
            "username": "test",
            "passphrase": "test",
            "output_path": "incoming",
        })
        icp = cls.env["ir.config_parameter"].sudo()
        icp.set_param("choreograph_sage_sale_account_export.sftp_ubl_server_id", cls.server.id)
        icp.set_param("choreograph_pa_supplier_ereporting.remote_path", False)

        cls.vendor = cls.env["res.partner"].create({
            "name": "SEREN SARN LTD",
            "is_company": True,
            "siren": "11005877",
            "pf_code_identification": " b2bint ",
            "vatex": "VATEX-EU-G",
        })
        cls.vendor_contact = cls.env["res.partner"].create({
            "name": "Contact SEREN",
            "parent_id": cls.vendor.id,
        })
        cls.other_vendor = cls.env["res.partner"].create({
            "name": "Fournisseur réforme",
            "is_company": True,
            "siren": "123456789",
            "pf_code_identification": "B2B",
            "vatex": "VATEX-EU-G",
        })
        cls.tax_exo = cls.env["account.tax"].create({
            "name": "Déductible Encaissement Exo - Asso",
            "type_tax_use": "purchase",
            "amount": 0.0,
            "unece_type_id": cls.env.ref("account_tax_unece.tax_type_vat").id,
            "unece_categ_id": cls.env.ref("account_tax_unece.tax_categ_z").id,
        })
        cls.tax_20 = cls.env["account.tax"].create({
            "name": "Déductible 20%",
            "type_tax_use": "purchase",
            "amount": 20.0,
            "unece_type_id": cls.env.ref("account_tax_unece.tax_type_vat").id,
            "unece_categ_id": cls.env.ref("account_tax_unece.tax_categ_s").id,
        })
        # On a copy of production, other documents are waiting: start from a clean state
        cls.env.cr.execute(
            "UPDATE account_move SET is_transferred_to_ereporting = TRUE WHERE move_type IN ('in_invoice', 'in_refund')")
        cls.env["account.move"].invalidate_model(["is_transferred_to_ereporting"])

    def _bill(self, move_type="in_invoice", partner=None, taxes=None, amounts=(100.0,),
              ref="INV-090726 CNX 3/3", provider_date="2026-08-20", post=True):
        move = self.init_invoice(
            move_type,
            partner=partner or self.vendor,
            invoice_date="2026-08-20",
            amounts=list(amounts),
            taxes=taxes if taxes is not None else self.tax_exo,
        )
        move.write({
            "ref": ref,
            "provider_invoice_date": provider_date,
            "invoice_date_due": "2026-09-19",
        })
        if post:
            move.action_post()
        return move

    def _run(self, sftp=None):
        sftp = sftp if sftp is not None else FakeSFTP()
        with patch.object(AccountMove, "get_sftp_client", return_value=(FakeSSH(), sftp)):
            report = self.env["account.move"].with_context(lang="en_US").export_ereporting_supplier_to_pa()
        return report, sftp

    def _read_csv(self, content):
        return list(csv.reader(io.StringIO(content.decode("utf-8")), delimiter="\t"))

    # ------------------------------------------------------------------

    @freeze_time("2026-11-16 05:00:00")
    def test_export_invoice_and_refund(self):
        invoice = self._bill()
        refund = self._bill("in_refund", amounts=(40.0,), ref="CN-001")
        # A follower with an email address must not be notified of the internal note
        follower = self.env["res.partner"].create({"name": "Abonné", "email": "abonne@example.com"})
        invoice.message_subscribe(partner_ids=follower.ids)
        report, sftp = self._run()
        self.assertFalse(self.env["mail.notification"].search([("res_partner_id", "=", follower.id)]))

        self.assertEqual(report.state, "success")
        self.assertEqual(report.type, "ereporting_supplier")
        self.assertEqual(report.file_name, "E-Reporting_Fournisseurs_16112026.csv")
        self.assertEqual((report.line_count, report.success_count, report.error_count), (2, 2, 0))
        self.assertEqual(report.exported_move_names, ", ".join(sorted([invoice.name, refund.name])))
        self.assertTrue(invoice.is_transferred_to_ereporting)
        self.assertTrue(refund.is_transferred_to_ereporting)
        note = invoice.message_ids.filtered(lambda m: "E-Reporting" in (m.body or ""))
        self.assertEqual(len(note), 1)
        self.assertEqual(note.subtype_id, self.env.ref("mail.mt_note"))
        self.assertIn("Sent on 16/11/2026 in the file E-Reporting_Fournisseurs_16112026.csv", note.body)

        content = sftp.files["ereporting/E-Reporting_Fournisseurs_16112026.csv"]
        self.assertEqual(report.attachment_id.raw, content)
        rows = self._read_csv(content)
        self.assertEqual(rows[0][0], "Numéro de la facture")
        self.assertEqual(len(rows[0]), 13)
        by_ref = {row[0]: row for row in rows[1:]}
        self.assertEqual(by_ref["INV-090726 CNX 3/3"], [
            "INV-090726 CNX 3/3", "20/08/2026", "19/09/2026", "Facture fournisseur",
            invoice.currency_id.name, "11005877", "489496331", "100.00", "0.00", "100.00",
            "Déductible Encaissement Exo - Asso", "Z", "VATEX-EU-G",
        ])
        self.assertEqual(by_ref["CN-001"][3], "Avoir fournisseur")
        self.assertEqual(by_ref["CN-001"][9], "40.00")

    def test_selection(self):
        draft = self._bill(post=False)
        other = self._bill(partner=self.other_vendor)
        done = self._bill()
        done.with_context(force_write=True).write({"is_transferred_to_ereporting": True})
        customer = self.init_invoice("out_invoice", partner=self.vendor, amounts=[100.0], post=True)
        from_contact = self._bill(partner=self.vendor_contact, ref="C-1")

        report, _sftp = self._run()

        self.assertEqual(report.exported_move_names, from_contact.name)
        for move in (draft, other, customer):
            self.assertFalse(move.is_transferred_to_ereporting)

    def test_missing_fields_are_errors(self):
        vendor_no_vatex = self.env["res.partner"].create({
            "name": "Particulier",
            "is_company": True,
            "siren": "999999999",
            "pf_code_identification": "B2C",
        })
        good = self._bill(ref="OK-1")
        no_date = self._bill(ref="KO-1", provider_date=False)
        no_vatex = self._bill(partner=vendor_no_vatex, ref="KO-2", provider_date=False)
        no_tax = self._bill(ref="KO-3", taxes=self.env["account.tax"])

        report, sftp = self._run()

        self.assertEqual(report.state, "partial")
        self.assertEqual((report.line_count, report.success_count, report.error_count), (4, 1, 3))
        self.assertEqual(report.exported_move_names, good.name)
        self.assertIn("%s : provider invoice date" % no_date.name, report.message)
        # Every missing value is listed at once
        self.assertIn("%s : provider invoice date, VATEX on the vendor Particulier" % no_vatex.name,
                      report.message)
        self.assertIn("%s : VAT (no tax on the invoice lines)" % no_tax.name, report.message)
        self.assertTrue(good.is_transferred_to_ereporting)
        for move in (no_date, no_vatex, no_tax):
            self.assertFalse(move.is_transferred_to_ereporting)
        rows = self._read_csv(list(sftp.files.values())[0])
        self.assertEqual([row[0] for row in rows[1:]], ["OK-1"])

    def test_all_in_error_sends_no_file(self):
        bad = self._bill(provider_date=False)
        report, sftp = self._run()
        self.assertEqual(report.state, "failed")
        self.assertFalse(sftp.files)
        self.assertFalse(report.attachment_id)
        self.assertFalse(bad.is_transferred_to_ereporting)

    def test_several_taxes_are_joined(self):
        move = self.init_invoice(
            "in_invoice", partner=self.vendor, invoice_date="2026-08-20", amounts=[100.0, 50.0],
            taxes=self.tax_exo)
        move.invoice_line_ids[1].tax_ids = self.tax_20
        move.write({"ref": "MULTI", "provider_invoice_date": "2026-08-20",
                    "invoice_date_due": "2026-09-19"})
        move.action_post()

        report, sftp = self._run()

        self.assertEqual(report.state, "success")
        row = self._read_csv(list(sftp.files.values())[0])[1]
        self.assertEqual(row[7:12], ["150.00", "10.00", "160.00",
                                     "Déductible Encaissement Exo - Asso / Déductible 20%", "Z / S"])

    def test_sftp_failure_marks_nothing(self):
        move = self._bill()
        with self.assertLogs("odoo.addons.choreograph_pa_supplier_ereporting", level="ERROR"):
            report, _sftp = self._run(FakeSFTP(fail=True))
        self.assertEqual(report.state, "failed")
        self.assertIn("Permission denied", report.message)
        self.assertTrue(report.attachment_id)
        self.assertFalse(report.exported_move_names)
        self.assertFalse(move.is_transferred_to_ereporting)
        self.assertFalse(move.message_ids.filtered(lambda m: "E-Reporting" in (m.body or "")))

    def test_no_sftp_server(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "choreograph_sage_sale_account_export.sftp_ubl_server_id", False)
        move = self._bill()
        with self.assertLogs("odoo.addons.choreograph_pa_supplier_ereporting", level="ERROR"):
            report, _sftp = self._run()
        self.assertEqual(report.state, "failed")
        self.assertIn("No SFTP server", report.message)
        self.assertFalse(move.is_transferred_to_ereporting)

    def test_nothing_to_export(self):
        report, sftp = self._run()
        self.assertEqual(report.state, "success")
        self.assertEqual(report.line_count, 0)
        self.assertFalse(sftp.files)

    @freeze_time("2026-11-16 05:00:00")
    def test_same_day_file_is_not_overwritten(self):
        move = self._bill()
        sftp = FakeSFTP({"ereporting/E-Reporting_Fournisseurs_16112026.csv": b"first"})
        report, sftp = self._run(sftp)
        self.assertEqual(report.file_name, "E-Reporting_Fournisseurs_16112026_2.csv")
        self.assertIn("E-Reporting_Fournisseurs_16112026_2.csv", move.message_ids[0].body)
        self.assertEqual(sftp.files["ereporting/E-Reporting_Fournisseurs_16112026.csv"], b"first")

    def test_custom_directory(self):
        self.env["ir.config_parameter"].sudo().set_param(
            "choreograph_pa_supplier_ereporting.remote_path", "/data/ereporting/")
        self._bill()
        _report, sftp = self._run()
        self.assertTrue(list(sftp.files)[0].startswith("/data/ereporting/E-Reporting_Fournisseurs_"))

    def test_file_name_uses_paris_date(self):
        # Monday 16/11 00:30 in Paris = Sunday 15/11 23:30 UTC
        with freeze_time("2026-11-15 23:30:00"):
            self.assertEqual(self.env["account.move"]._get_ereporting_file_name(),
                             "E-Reporting_Fournisseurs_16112026.csv")

    def test_go_live_fills_provider_invoice_date(self):
        in_scope = self._bill(ref="NODATE", provider_date=False)
        other = self._bill(partner=self.other_vendor, ref="OTHER", provider_date=False)
        draft = self._bill(ref="DRAFT", provider_date=False, post=False)
        filled = self._bill(ref="FILLED", provider_date="2026-08-01")
        due_date = in_scope.invoice_date_due

        fill_provider_invoice_date(self.env.cr)
        self.env.invalidate_all()

        self.assertEqual(in_scope.provider_invoice_date, in_scope.invoice_date)
        # Only the date changes: the due date of the posted document is not recomputed
        self.assertEqual(in_scope.invoice_date_due, due_date)
        self.assertFalse(other.provider_invoice_date)
        self.assertFalse(draft.provider_invoice_date)
        self.assertEqual(str(filled.provider_invoice_date), "2026-08-01")

    def test_go_live_marks_documents_without_vat(self):
        without_vat = self._bill(ref="NOVAT")
        with_vat = self._bill(ref="VAT", taxes=self.tax_20)
        other = self._bill(partner=self.other_vendor, ref="OTHER")
        post_init_hook(self.env.cr, self.env.registry)
        self.assertTrue(without_vat.is_transferred_to_ereporting)
        self.assertFalse(with_vat.is_transferred_to_ereporting)
        self.assertFalse(other.is_transferred_to_ereporting)
