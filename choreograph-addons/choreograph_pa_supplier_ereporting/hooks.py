# -*- coding: utf-8 -*-

import logging

from odoo import SUPERUSER_ID, api

from .models.account_move import EREPORTING_MOVE_TYPES, EREPORTING_PF_CODES

_logger = logging.getLogger(__name__)


def fill_provider_invoice_date(cr):
    """Copy the invoice date into the empty provider invoice date of the posted
    supplier documents of B2C / B2BINT vendors, so that they can be exported.

    SQL on purpose: through the ORM, the due date of each posted document would be
    recomputed from the new date. Here only provider_invoice_date changes.
    """
    cr.execute(
        """
        UPDATE account_move am
           SET provider_invoice_date = am.invoice_date
          FROM res_partner p
         WHERE p.id = am.commercial_partner_id
           AND am.move_type IN %s
           AND am.state = 'posted'
           AND am.provider_invoice_date IS NULL
           AND am.invoice_date IS NOT NULL
           AND upper(trim(p.pf_code_identification)) IN %s
     RETURNING am.id
        """,
        (EREPORTING_MOVE_TYPES, EREPORTING_PF_CODES),
    )
    move_ids = [row[0] for row in cr.fetchall()]
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["account.move"].browse(move_ids).invalidate_recordset(["provider_invoice_date"])
    _logger.info("E-Reporting: provider invoice date filled from the invoice date on %s "
                 "supplier document(s): %s", len(move_ids), move_ids)
    return move_ids


def post_init_hook(cr, registry):
    """At go-live, fill the missing provider invoice dates, then mark the posted
    supplier documents without VAT as transferred.

    Documents with VAT stay unmarked and go out with the first export.
    """
    fill_provider_invoice_date(cr)
    env = api.Environment(cr, SUPERUSER_ID, {})
    move_model = env["account.move"]
    moves = move_model.search(move_model._get_ereporting_domain() + [("amount_tax", "=", 0)])
    if moves:
        # SQL: the account.move write of choreograph_sox only accepts one record at a time
        cr.execute(
            "UPDATE account_move SET is_transferred_to_ereporting = TRUE WHERE id IN %s",
            (tuple(moves.ids),),
        )
        moves.invalidate_recordset(["is_transferred_to_ereporting"])
    _logger.info("E-Reporting: %s supplier document(s) without VAT marked as transferred", len(moves))
