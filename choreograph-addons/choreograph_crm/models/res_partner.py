# -*- coding: utf-8 -*-
from odoo import models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def name_get(self):
        params = self.env.context.get('params', {})
        if params.get('model', False) == 'crm.lead' and params.get('view_type', False) == 'kanban':
            return [(partner.id, partner.display_name) for partner in self]
        return super().name_get()
