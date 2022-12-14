# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 ArkeUp (<http://www.arkeup.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import http
from odoo.addons.web.controllers.home import Home
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class Home(Home):

    @http.route()
    def index(self, *args, **kw):
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user.is_portal_user:
            if user.check_active_subscription():
                return request.redirect('/operation/indication')
            return request.redirect('/web/session/logout')
        return super(Home, self).index(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        user = request.env['res.users'].sudo().browse(uid)
        if not redirect and user.is_portal_user:
            if user.check_active_subscription():
                return '/operation/indication'
            return '/web/session/logout'
        return super(Home, self)._login_redirect(uid, redirect=redirect)

    @http.route('/link', type='http', auth="public", website=True)
    def index_link(self, *args, **kw):
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user:
            if user.is_portal_user:
                if user.check_active_subscription():
                    return request.redirect('/operation/indication')
                return request.redirect('/web/session/logout')
            return request.redirect('/')
        else:
            return request.redirect('web/login')


class CustomerPortal(CustomerPortal):

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user.is_portal_user:
            if user.check_active_subscription() and not user._password_has_expired():
                return request.redirect('/operation/list')
            return request.redirect('/web/session/logout')
        return request.redirect('/')
