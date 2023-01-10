# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTask(models.Model):
    _inherit = 'project.task'

    role_id = fields.Many2one('res.role', 'Role')

    @api.onchange('role_id')
    def onchange_role_id(self):
        partner_role = self.project_id.partner_id.role_ids.filtered(lambda r: r.role_id.id == self.role_id.id)
        self.user_ids = [(6, 0, self.role_id and self.project_id.partner_id and partner_role and partner_role[0].user_ids.ids or [])]
