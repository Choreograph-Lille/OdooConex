# -*- coding: utf-8 -*-

from .tools import clean_dict
from odoo import models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def execute_query(self, query=None):
        if not query:
            return False
        self._cr.execute(query)
        result = []
        for data in self._cr.dictfetchall():
            result.append(clean_dict(data))
        return result
