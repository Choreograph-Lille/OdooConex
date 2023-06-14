# -*- coding: utf-8 -*-
from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def name_get(self):
        if self.env.context.get('name_get_custom', False):
            return [(partner.id, partner.display_name) for partner in self]
        return super().name_get()
