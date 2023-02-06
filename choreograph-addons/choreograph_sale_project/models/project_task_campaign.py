from odoo import fields, models, api


class ProjectTaskCampaign(models.Model):
    _name = 'project.task.campaign'

    name = fields.Char('Campaign Name')
    id_campaign = fields.Char('Campaign ID')
    task_id = fields.Many2one('project.task')

