# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug

from odoo import http, _
from odoo.http import request
from odoo.addons.website.controllers.main import Website

_logger = logging.getLogger(__name__)


class MaasWebsiteBase(Website):

    @http.route()
    def web_login(self, redirect=None, *args, **kw):
        response = super(Website, self).web_login(redirect=redirect, *args, **kw)
        if not redirect and request.params['login_success']:
            if request.env['res.users'].browse(request.uid).state == 'active':
                return response
            else:
                redirect = '/'
            return http.request.redirect(redirect)
        return response
