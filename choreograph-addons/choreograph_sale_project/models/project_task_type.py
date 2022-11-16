# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProjectTaskType(models.Model):
    _name = 'choreograph.project.task.type'

    name = fields.Char('Name')
