from odoo import fields, models

TASK_NUMBER = [(str(n), str(n)) for n in range(5, 100, 5)]


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_type_id = fields.Many2one('choreograph.project.task.type', string='Task type')
    task_number = fields.Selection(TASK_NUMBER)
    is_template = fields.Boolean(related='project_id.is_template')
