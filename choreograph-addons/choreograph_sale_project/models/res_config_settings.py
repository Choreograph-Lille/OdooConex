# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    survey_exchange_char_limit = fields.Integer(
        config_parameter="choreograph_sale_project.survey_exchange_char_limit",
        default=100
    )