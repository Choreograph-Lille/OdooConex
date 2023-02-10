from odoo import fields, models

STAGE_NUMBER = [(str(n), str(n)) for n in range(10, 100, 10)]


class ProjectProjectStage(models.Model):
    _inherit = 'project.project.stage'

    stage_number = fields.Selection(STAGE_NUMBER)
