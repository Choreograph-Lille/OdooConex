# -*- encoding: utf-8 -*-

from odoo import _, http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.web.controllers.home import Home


class Home(Home):

    @http.route()
    def index(self, *args, **kw):
        # if request.env.user and request.env.user.has_group('base.group_user'):
        #     return request.redirect('/home/bo')
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user.share:
            if user.check_active_subscription():
                return request.redirect('/operation/list')
            return request.redirect('/web/session/logout')
        return super(Home, self).index(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        user = request.env['res.users'].sudo().browse(uid)
        if not redirect and user.share:
            if user.check_active_subscription():
                return '/operation/list'
            return '/web/session/logout'
        return super(Home, self)._login_redirect(uid, redirect=redirect)

    @http.route('/link', type='http', auth="public", website=True)
    def index_link(self, *args, **kw):
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user:
            if user.share:
                if user.check_active_subscription():
                    return request.redirect('/operation/list')
                return request.redirect('/web/session/logout')
            return request.redirect('/')
        else:
            return request.redirect('web/login')


class CustomerPortal(CustomerPortal):

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user.share:
            if user.check_active_subscription():
                return request.redirect('/operation/list')
            return request.redirect('/web/session/logout')
        return request.redirect('/web')
