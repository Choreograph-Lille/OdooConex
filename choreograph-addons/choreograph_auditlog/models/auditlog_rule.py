from odoo import api, models


class AuditlogRule(models.Model):
    _inherit = 'auditlog.rule'

    @api.model
    def auto_subscribe(self):
        datas = [
            self.env.ref('choreograph_auditlog.auditlog_sox_roles').id,
            self.env.ref('choreograph_auditlog.auditlog_res_bank').id,
            self.env.ref('choreograph_auditlog.auditlog_res_partner').id,
            self.env.ref('choreograph_auditlog.auditlog_account_move').id,
            self.env.ref('choreograph_auditlog.auditlog_sale_order').id,
        ]
        rule_ids = self.browse(datas).filtered(lambda rule: rule.state == 'draft')
        rule_ids.subscribe()
