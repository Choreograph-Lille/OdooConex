from odoo import http

from odoo.addons.maas_base.controllers.main import MaasWebsiteBase
from odoo.addons.website.controllers.main import Website

class WebsiteCnx(MaasWebsiteBase):

    @http.route('/web/bo/login', website=True, auth="public", sitemap=False)
    def web_native_login(self, *args, **kw):
        return Website().web_login(*args, **kw)
