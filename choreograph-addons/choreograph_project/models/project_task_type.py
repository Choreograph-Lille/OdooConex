from odoo import fields, models
from .project_project_stage import STAGE_NUMBER


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    stage_number = fields.Selection(STAGE_NUMBER)
