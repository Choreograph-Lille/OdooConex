from odoo import fields, models


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    is_auditreport = fields.Boolean()
    auditlog_model_id = fields.Many2one('ir.model')
