# -*- encoding: utf-8 -*-
from odoo import models
from odoo.http import Response

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls, endpoint):
        """Override _dispatch method"""
        response = super()._dispatch(endpoint)

        if isinstance(response, Response):
            response.headers['Cache-Control'] = 'max-age=0, no-cache, no-store'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            print(response.headers)
        return response
