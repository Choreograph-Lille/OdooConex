# -*- coding: utf-8 -*-

from odoo import fields, models


class ProjectTaskCampaign(models.Model):
    _name = 'project.task.campaign'

    name = fields.Char('Campaign Name')
    id_campaign = fields.Char('Campaign ID')
    task_id = fields.Many2one('project.task')
