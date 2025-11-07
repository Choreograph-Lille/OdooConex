# -*- encoding: utf-8 -*-
from odoo import models
from odoo.http import Response
from odoo.http import request

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _dispatch(cls, endpoint):
        """Override _dispatch method"""
        response = super()._dispatch(endpoint)
        base_url = request.httprequest.url_root.strip('/') or request.env.user.get_base_url()
        

        if isinstance(response, Response):
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
            response.headers['X-Frame-Options'] = 'SAMEORIGIN'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            response.headers['Permissions-Policy'] = (
                'geolocation=(), microphone=(), camera=(), payment=()'
            )
            
            response.headers['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "font-src 'self'; "
                "frame-ancestors 'self'; "
                "report-to csp-endpoint;"
            )
            response.headers['Report-To'] = (
                '{"group":"csp-endpoint","max_age":10886400,'
                f'"endpoints":[{{"url":"{base_url}/csp-report"}}]'
            )
    
        return response
