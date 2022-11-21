# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug

from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.http import request
from odoo.addons.password_security.controllers.main import PasswordSecurityHome
from odoo.addons.website.controllers.main import Website

_logger = logging.getLogger(__name__)


class AuthSignupHomeAlert(PasswordSecurityHome):

    @http.route()
    def web_auth_reset_password(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()
        if (
                request.httprequest.method == 'POST' and
                qcontext.get('login') and
                'error' not in qcontext and
                'token' not in qcontext
        ):
            login = qcontext.get('login')
            user_ids = request.env.sudo().search(
                [('login', '=', login)],
                limit=1,
            )
            if not user_ids:
                user_ids = request.env.sudo().search(
                    [('email', '=', login)],
                    limit=1,
                )
            user_ids._validate_pass_reset()
        login = qcontext.get('login')
        user_ids = http.request.env['res.users'].sudo().search(['|', ('login', '=', login), ('email', '=', login)],
                                                               limit=1,)
        if user_ids and user_ids._password_has_expired() and user_ids.state != 'new':
            qcontext['expired'] = True
        elif user_ids and not user_ids._password_has_expired():
            qcontext['expired'] = False

        if not qcontext.get('token') and not qcontext.get('reset_password_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                if qcontext.get('token'):
                    self.do_signup(qcontext)
                    return super(AuthSignupHomeAlert, self).web_login(*args, **kw)
                else:
                    login = qcontext.get('login')
                    assert login, _("No login provided.")
                    _logger.info(
                        "Password reset attempt for <%s> by user <%s> from %s",
                        login, request.env.user.login, request.httprequest.remote_addr)
                    request.env['res.users'].sudo().reset_password(login)
                    qcontext['message'] = _("An email has been sent with credentials to reset your password")
            except SignupError:
                qcontext['error'] = _("Could not reset your password")
                _logger.exception('error when resetting password')
            except Exception as e:
                if hasattr(e, 'name'):
                    qcontext['error'] = str(e.name)
                elif not hasattr(e, 'name') and hasattr(e, 'message'):
                    qcontext['error'] = str(e.message)
                else:
                    qcontext['error'] = str(e)

        response = request.render('auth_signup.reset_password', qcontext)
        response.headers['X-Frame-Options'] = 'DENY'
        return response


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
