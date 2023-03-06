from .project_project_stage import STAGE_NUMBER
from .project_project import TYPE_OF_PROJECT
from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    stage_number = fields.Selection(STAGE_NUMBER)
    type_of_project = fields.Selection(TYPE_OF_PROJECT, default='standard', required=True)
