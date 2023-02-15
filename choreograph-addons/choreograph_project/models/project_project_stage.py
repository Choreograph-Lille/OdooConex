from .project_project import PROJECT_OPERATION_TYPE
from odoo import fields, models

STAGE_NUMBER = [(str(n), str(n)) for n in range(10, 100, 10)]


class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'

    stage_number = fields.Selection(STAGE_NUMBER)
    project_operation_type = fields.Selection(PROJECT_OPERATION_TYPE, default='standard', required=True)
