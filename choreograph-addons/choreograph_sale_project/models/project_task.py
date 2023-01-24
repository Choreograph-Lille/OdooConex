# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

TASK_NUMBER = [('5', '5'), ('10', '10'), ('15', '15'), ('20', '20'), ('25', '25'), ('30', '30'), ('35', '35'), ('40', '40'), ('45', '45'), ('50', '50'), ('60', '60'), ('65', '65'), ('70', '70'), ('75', '75'), ('80', '80'), ('85', '85'), ('90', '90'), ('95', '95')]


class ProjectTask(models.Model):
    _inherit = 'project.task'

    task_type_id = fields.Many2one('choreograph.project.task.type', string='Task type')
    task_number = fields.Selection(TASK_NUMBER, 'Task Number')
    is_template = fields.Boolean(related='project_id.is_template')
