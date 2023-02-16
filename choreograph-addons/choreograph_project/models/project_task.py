from .project_project import PROJECT_OPERATION_TYPE, filter_by_project_operation_type
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    role_id = fields.Many2one('res.role', 'Role')

    project_operation_type = fields.Selection(
        PROJECT_OPERATION_TYPE, default='standard', required=True, compute='_compute_project_operation_type', store=True, readonly=False)

    @api.onchange('role_id')
    def onchange_role_id(self):
        partner_role = self.project_id.partner_id.role_ids.filtered(lambda r: r.role_id.id == self.role_id.id)
        self.user_ids = [
            (6, 0, self.role_id and self.project_id.partner_id and partner_role and partner_role[0].user_ids.ids or [])]

    @api.depends('project_id')
    def _compute_project_operation_type(self):
        for rec in self:
            rec.project_operation_type = rec.project_id.project_operation_type if rec.project_id else 'standard'

    @api.model
    @filter_by_project_operation_type
    def _read_group_stage_ids(self, stages, domain, order):
        return super()._read_group_stage_ids(stages, domain, order)

    @api.model
    @filter_by_project_operation_type
    def _read_group_personal_stage_type_ids(self, stages, domain, order):
        return super()._read_group_personal_stage_type_ids(stages, domain, order)
