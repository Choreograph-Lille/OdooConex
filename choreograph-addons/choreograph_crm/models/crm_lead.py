# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sox = fields.Boolean('SOX')
    activity_sector = fields.Char('Activity sector')
    category_name = fields.Char('Category name')

