# -*- coding: utf-8 -*-
from odoo import models


class BaseModel(models.AbstractModel):
    _inherit = 'base'

    def get_base_url(self):
        if self._context.get('user_url', False) == 'gao':
            return self.env['ir.config_parameter'].sudo().get_param('web.gao.url')
        return super().get_base_url()
