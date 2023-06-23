# -*- coding: utf-8 -*-

from odoo import models, fields


class SpreadsheetCollaborativeMixin(models.AbstractModel):
    _inherit = "spreadsheet.collaborative.mixin"

    spreadsheet_revision_ids = fields.One2many(groups="base.group_user", )
