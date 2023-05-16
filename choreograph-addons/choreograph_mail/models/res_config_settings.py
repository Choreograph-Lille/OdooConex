# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    disable_followers = fields.Boolean('Disable customer subscription on a model',
                                       readonly=False,
                                       related='company_id.disable_followers')
