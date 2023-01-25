from odoo import fields, models


class ProjectTaskType(models.Model):
    _name = 'choreograph.project.task.type'
    _description = 'Project Task Type'

    name = fields.Char()
