# -*- coding: utf-8 -*-

import io
from unittest.mock import patch

from freezegun import freeze_time

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.choreograph_sage_sftp_import.models.account_move import AccountMove
from odoo.tests import tagged

HEADER = "Référence Pièce\tSiren tiers\tStatut paiement\tDate paiement\tMontant payé\tMontant restant dû\tDevise\tID ODOO"


class FakeSFTP:
    def __init__(self, files):
        self.files = files

    def listdir(self, path):
        return list(self.files)

    def open(self, path, mode="rb"):
        name = path.rsplit("/", 1)[-1]
        if name not in self.files:
            raise FileNotFoundError(path)
        return io.BytesIO(self.files[name])


class FakeSSH:
    def __init__(self, sftp):
        self.sftp = sftp
        self.closed = False

    def open_sftp(self):
        return self.sftp

    def close(self):
        self.closed = True


@tagged("post_install", "-at_install")
class TestSageImport(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref="l10n_fr.l10n_fr_pcg_chart_template"):
        # French chart: l10n_generic_coa is not installed on Choreograph databases
        super().setUpClass(chart_template_ref=chart_template_ref)
        # 'Immediate Payment' is tied to the Choreograph company: share it with the test company
        cls.pay_terms_a.sudo().company_id = False
        cls.server = cls.env["choreograph.sage.sftp.server"].create({
            "name": "Sage test",
            "host": "localhost",
            "username": "test",
            "passphrase": "test",
            "output_path": "Output",
        })
        icp = cls.env["ir.config_parameter"].sudo()
        icp.set_param("choreograph_sage_sftp_import.sftp_server_id", cls.server.id)
        icp.set_param("choreograph_sage_sale_account.prefix", "PAYVEN")
        icp.set_param("choreograph_sage_sale_account.sage_file_date", False)
        icp.set_param("choreograph_sage_purchase_account.prefix", "PAYACH")
        icp.set_param("choreograph_sage_purchase_account.sage_file_date", False)
        icp.set_param("choreograph_sage_sftp_import.catchup_days", 30)
        # The production journal belongs to CHOREOGRAPH: use the test company's bank journal
        icp.set_param("choreograph_sage_purchase_account.purchase_default_journal_id",
                      cls.company_data["default_journal_bank"].id)
        cls.sale_move = cls.env["account.move"].with_context(move_type="out_invoice")
        # On a copy of production, existing logs would mark the test files as read.
        # Start from an empty history (the deletion is rolled back after the tests)
        cls.env["sftp.import.report"].sudo().search([]).unlink()

    def _run(self, files, move_type="out_invoice", log_type="sale"):
        ssh = FakeSSH(FakeSFTP(files))
        with patch.object(AccountMove, "get_sftp_client_import", return_value=ssh):
            # The crons run as __system__: record rules do not apply
            self.env["account.move"].sudo()._run_sage_import(move_type, log_type)
        return ssh

    def _logs(self, log_type="sale"):
        return self.env["sftp.import.report"].search([("type", "=", log_type)], order="id")

    # ------------------------------------------------------------------
    # File date / name
    # ------------------------------------------------------------------

    def test_file_name_winter_time(self):
        # 03/11 01:00 in Paris (UTC+1) = 03/11 00:00 UTC -> file of 02/11 expected
        with freeze_time("2026-11-03 00:00:30"):
            self.assertEqual(self.sale_move.get_file_name(), "PAYVEN_20261102.csv")

    def test_file_name_summer_time(self):
        # 16/10 01:00 in Paris (UTC+2) = 15/10 23:00 UTC -> file of 15/10 expected
        with freeze_time("2026-10-15 23:00:30"):
            self.assertEqual(self.sale_move.get_file_name(), "PAYVEN_20261015.csv")

    def test_forced_date_is_converted_to_french_date(self):
        # 'Date import' = 02/11 00:00 in Paris, stored in UTC as 01/11 23:00
        self.env["ir.config_parameter"].sudo().set_param(
            "choreograph_sage_sale_account.sage_file_date", "2026-11-01 23:00:00")
        self.assertEqual(self.sale_move.get_file_name(), "PAYVEN_20261102.csv")
        self.assertEqual(
            self.sale_move._get_sage_files_to_import(self.server, [], "sale"),
            ["PAYVEN_20261102.csv"])

    # ------------------------------------------------------------------
    # Catch-up selection
    # ------------------------------------------------------------------

    @freeze_time("2026-11-05 00:00:30")
    def test_catchup_selection(self):
        list_dir = [
            "PAYVEN_20260901.csv",  # out of the 30-day window
            "PAYVEN_20261025.csv",
            "PAYVEN_20261026.csv",  # already read
            "PAYVEN_20261102.csv",
            "PAYVEN_20261104.csv",
            "PAYVEN_20261105.csv",  # today: may still be in transfer
            "PAYACH_20261102.csv",  # purchase file
            "other.txt",
        ]
        self.env["sftp.import.report"].create({
            "type": "sale", "file_name": "PAYVEN_20261026.csv", "sftp_server_id": self.server.id})
        # a log of the purchase flow must not hide a sale file
        self.env["sftp.import.report"].create({
            "type": "purchase", "file_name": "PAYVEN_20261102.csv", "sftp_server_id": self.server.id})
        self.assertEqual(
            self.sale_move._get_sage_files_to_import(self.server, list_dir, "sale"),
            ["PAYVEN_20261025.csv", "PAYVEN_20261102.csv", "PAYVEN_20261104.csv"])

    @freeze_time("2026-11-05 00:00:30")
    def test_catchup_days_parameter(self):
        self.env["ir.config_parameter"].sudo().set_param("choreograph_sage_sftp_import.catchup_days", 3)
        list_dir = ["PAYVEN_20261101.csv", "PAYVEN_20261102.csv", "PAYVEN_20261104.csv"]
        self.assertEqual(
            self.sale_move._get_sage_files_to_import(self.server, list_dir, "sale"),
            ["PAYVEN_20261102.csv", "PAYVEN_20261104.csv"])

    @freeze_time("2026-11-05 00:00:30")
    def test_catchup_days_parameter_invalid(self):
        self.env["ir.config_parameter"].sudo().set_param("choreograph_sage_sftp_import.catchup_days", "abc")
        self.assertEqual(self.sale_move._get_sage_catchup_days(), 30)

    # ------------------------------------------------------------------
    # End-to-end
    # ------------------------------------------------------------------

    def _make_file(self, invoices):
        rows = [HEADER] + [
            f"{inv.name}\t\tEn paiement\t30/10/2026\t{inv.amount_total:.2f}\t0.00\t{inv.currency_id.name}\t{inv.id}"
            for inv in invoices
        ]
        return ("﻿" + "\r\n".join(rows) + "\r\n").encode("utf-8")

    @freeze_time("2026-11-05 00:00:30")
    def test_import_catches_up_missed_files(self):
        inv1 = self.init_invoice("out_invoice", amounts=[100.0], post=True)
        inv2 = self.init_invoice("out_invoice", amounts=[200.0], post=True)
        files = {
            "PAYVEN_20261102.csv": self._make_file(inv1),
            "PAYVEN_20261103.csv": self._make_file(inv2),
        }
        ssh = self._run(files)

        self.assertTrue(ssh.closed)
        logs = self._logs()
        self.assertEqual(logs.mapped("file_name"), ["PAYVEN_20261102.csv", "PAYVEN_20261103.csv"])
        self.assertEqual(logs.mapped("state"), ["success", "success"])
        self.assertEqual(inv1.amount_residual, 0.0)
        self.assertEqual(inv2.amount_residual, 0.0)
        # The payment is dated with the Sage payment date, not the import date
        self.assertEqual(inv1._get_reconciled_payments().date.isoformat(), "2026-10-30")

        # Next run: nothing new, files are not imported twice
        self._run(files)
        last = self._logs()[-1]
        self.assertEqual(last.state, "success")
        self.assertFalse(last.file_name)
        self.assertFalse(last.error_line_ids)
        self.assertIn("30", last.message)
        self.assertEqual(len(inv1._get_reconciled_payments()), 1)

    @freeze_time("2026-11-05 00:00:30")
    def test_import_purchase_file(self):
        bill = self.init_invoice("in_invoice", amounts=[150.0], post=True)
        bill.ref = "BILL-001"
        rows = [HEADER, f"BILL-001\t\tEn paiement\t02/11/2026\t{bill.amount_total:.2f}\t0.00\t{bill.currency_id.name}\t{bill.id}"]
        files = {"PAYACH_20261102.csv": ("﻿" + "\r\n".join(rows)).encode("utf-8")}
        self._run(files, move_type="in_invoice", log_type="purchase")
        log = self._logs("purchase")
        self.assertEqual(log.file_name, "PAYACH_20261102.csv")
        self.assertEqual(log.state, "success")
        self.assertEqual(bill.amount_residual, 0.0)

    def _pay_manually(self, invoice):
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids,
        ).create({})._create_payments()

    @freeze_time("2026-11-05 00:00:30")
    def test_already_paid_line_is_ignored(self):
        # Customer invoices paid manually by the accounting team before the import
        inv_paid = self.init_invoice("out_invoice", amounts=[100.0], post=True)
        inv_todo = self.init_invoice("out_invoice", amounts=[200.0], post=True)
        self._pay_manually(inv_paid)
        files = {
            "PAYVEN_20261102.csv": self._make_file(inv_paid),            # only already paid lines
            "PAYVEN_20261103.csv": self._make_file(inv_paid + inv_todo),  # mixed
        }
        self._run(files)
        logs = self._logs()
        self.assertEqual(logs.mapped("state"), ["success", "success"])
        self.assertEqual(logs.mapped("error_count"), [0, 0])
        self.assertEqual(logs.mapped("success_count"), [0, 1])
        self.assertEqual(set(logs.error_line_ids.mapped("error_type")), {"already_paid"})
        self.assertTrue(all(logs.mapped("message")))
        # The invoice already paid gets no second payment, the other one is now paid
        self.assertEqual(len(inv_paid._get_reconciled_payments()), 1)
        self.assertEqual(inv_todo.amount_residual, 0.0)

    @freeze_time("2026-11-05 00:00:30")
    def test_already_paid_with_other_amount_is_an_error(self):
        inv = self.init_invoice("out_invoice", amounts=[100.0], post=True)
        self._pay_manually(inv)
        row = f"{inv.name}\t\tEn paiement\t30/10/2026\t{inv.amount_total + 10:.2f}\t0.00\t{inv.currency_id.name}\t{inv.id}"
        files = {"PAYVEN_20261102.csv": ("﻿" + HEADER + "\r\n" + row + "\r\n").encode("utf-8")}
        self._run(files)
        log = self._logs()
        self.assertEqual(log.state, "failed")
        self.assertEqual(log.error_line_ids.error_type, "data_mismatch")

    @freeze_time("2026-11-05 00:00:30")
    def test_invalid_file_is_logged_and_not_retried(self):
        inv = self.init_invoice("out_invoice", amounts=[100.0], post=True)
        files = {
            "PAYVEN_20261102.csv": "﻿col1\tcol2\r\na\tb\r\n".encode("utf-8"),  # missing columns
            "PAYVEN_20261103.csv": self._make_file(inv),
        }
        self._run(files)
        logs = self._logs()
        self.assertEqual(logs.mapped("state"), ["rejected", "success"])
        self.assertEqual(logs[0].file_name, "PAYVEN_20261102.csv")
        self.assertEqual(inv.amount_residual, 0.0)

        self._run(files)
        self.assertEqual(len(self._logs()), 3)  # only one more "no new file" log

    @freeze_time("2026-11-05 00:00:30")
    def test_empty_file_is_success(self):
        # Sage writes a header-only file on days without payment
        files = {"PAYVEN_20261102.csv": ("﻿" + HEADER + "\r\n").encode("utf-8")}
        self._run(files)
        log = self._logs()
        self.assertEqual(log.file_name, "PAYVEN_20261102.csv")
        self.assertEqual(log.state, "success")
        self.assertEqual(log.line_count, 0)
        self.assertFalse(log.error_line_ids)
        self.assertTrue(log.message)

    def test_amount_compared_with_currency_rounding(self):
        inv = self.init_invoice("out_invoice", amounts=[100.0], taxes=[], post=True)
        log = self.env["sftp.import.report"].create({"type": "sale", "sftp_server_id": self.server.id})

        def row(amount):
            return {
                "Référence Pièce": inv.name, "Statut paiement": "En paiement", "Siren tiers": "",
                "Montant payé": amount, "Devise": inv.currency_id.name, "ID ODOO": str(inv.id),
            }

        # Float noise below the currency rounding: accepted
        self.assertEqual(self.sale_move.validate_data_import(row("100.0000000001"), log, "out_invoice"), inv)
        # One cent difference: rejected
        self.assertFalse(self.sale_move.validate_data_import(row("100.01"), log, "out_invoice"))
        self.assertEqual(log.error_line_ids.error_type, "data_mismatch")
