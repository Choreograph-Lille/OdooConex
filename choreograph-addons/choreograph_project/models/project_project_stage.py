from .project_project import TYPE_OF_PROJECT
from odoo import fields, models

STAGE_NUMBER = [(str(n), str(n)) for n in range(10, 100, 10)] + [('15', '15'), ('25', '25')]


class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'

    stage_number = fields.Selection(STAGE_NUMBER)
    type_of_project = fields.Selection(TYPE_OF_PROJECT, default='standard', required=True)
