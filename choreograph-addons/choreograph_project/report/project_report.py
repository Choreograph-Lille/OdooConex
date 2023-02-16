from odoo import fields, models
from ..models.project_project import PROJECT_OPERATION_TYPE


class ProjectReport(models.Model):
    _inherit = 'report.project.task.user'

    project_operation_type = fields.Selection(PROJECT_OPERATION_TYPE, default='standard', required=True)

    def _select(self):
        return super()._select() + ", t.project_operation_type as project_operation_type"

    def _group_by(self):
        return super()._group_by() + ", t.project_operation_type"
