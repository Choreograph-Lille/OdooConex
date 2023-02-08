# -*- encoding: utf-8 -*-

import odoo
from odoo import _, http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.web.controllers.home import SIGN_UP_REQUEST_PARAMS, Home
from odoo.addons.web.controllers.utils import ensure_db


class Home(Home):

    @http.route()
    def index(self, *args, **kw):
        # if request.env.user and request.env.user.has_group('base.group_user'):
        #     return request.redirect('/home/bo')
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user.share:
            if user.check_active_subscription():
                return request.redirect('/operation/indication')
            return request.redirect('/web/session/logout')
        return super(Home, self).index(*args, **kw)

    def _login_redirect(self, uid, redirect=None):
        user = request.env['res.users'].sudo().browse(uid)
        if not redirect and user.share:
            if user.check_active_subscription():
                return '/operation/indication'
            return '/web/session/logout'
        return super(Home, self)._login_redirect(uid, redirect=redirect)

    @http.route('/link', type='http', auth="public", website=True)
    def index_link(self, *args, **kw):
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user:
            if user.share:
                if user.check_active_subscription():
                    return request.redirect('/operation/indication')
                return request.redirect('/web/session/logout')
            return request.redirect('/')
        else:
            return request.redirect('web/login')

    @http.route('/web/login', website=True, auth="public", sitemap=False)
    def web_native_login(self, redirect=None, **kw):
        ensure_db()
        request.params['login_success'] = False
        if request.httprequest.method == 'GET' and redirect and request.session.uid:
            return request.redirect(redirect)

        # so it is correct if overloaded with auth="public"
        if not request.uid:
            request.update_env(user=odoo.SUPERUSER_ID)

        values = {k: v for k, v in request.params.items() if k in SIGN_UP_REQUEST_PARAMS}
        try:
            values['databases'] = http.db_list()
        except odoo.exceptions.AccessDenied:
            values['databases'] = None

        if request.httprequest.method == 'POST':
            try:
                uid = request.session.authenticate(request.db, request.params['login'], request.params['password'])
                request.params['login_success'] = True
                return request.redirect(self._login_redirect(uid, redirect=redirect))
            except odoo.exceptions.AccessDenied as e:
                if e.args == odoo.exceptions.AccessDenied().args:
                    values['error'] = _("Wrong login/password")
                else:
                    values['error'] = e.args[0]
        else:
            if 'error' in request.params and request.params.get('error') == 'access':
                values['error'] = _('Only employees can access this database. Please contact the administrator.')

        if 'login' not in values and request.session.get('auth_login'):
            values['login'] = request.session.get('auth_login')

        if not odoo.tools.config['list_db']:
            values['disable_database_manager'] = True

        response = request.render('maas_website.login', values)
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
        return response


class CustomerPortal(CustomerPortal):

    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        user = request.env['res.users'].sudo().browse(request.session.uid)
        if user.share:
            if user.check_active_subscription():
                return request.redirect('/operation/list')
            return request.redirect('/web/session/logout')
        return request.redirect('/web')
