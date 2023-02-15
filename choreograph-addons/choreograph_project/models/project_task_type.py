from .project_project_stage import STAGE_NUMBER
from .project_project import PROJECT_OPERATION_TYPE
from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    stage_number = fields.Selection(STAGE_NUMBER)
    project_operation_type = fields.Selection(PROJECT_OPERATION_TYPE, default='standard', required=True)
