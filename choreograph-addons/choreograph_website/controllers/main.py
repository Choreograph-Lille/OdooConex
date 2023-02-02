from odoo import http

from odoo.addons.portal.controllers.web import Home


class Website(Home):

    @http.route('/web/bo/login', website=True, auth="public", sitemap=False)
    def web_login(self, *args, **kw):
        return super().web_login(*args, **kw)
