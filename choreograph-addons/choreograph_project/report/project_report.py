from odoo import fields, models
from ..models.project_project import TYPE_OF_PROJECT


class ProjectReport(models.Model):
    _inherit = 'report.project.task.user'

    type_of_project = fields.Selection(TYPE_OF_PROJECT, default='standard', required=True)

    def _select(self):
        return super()._select() + ", t.type_of_project as type_of_project"

    def _group_by(self):
        return super()._group_by() + ", t.type_of_project"
