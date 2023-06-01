from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    menu_ids = env['website.menu'].search([('url', '=', '/')])
    for menu in menu_ids:
        menu.write({
            'url': '/home/bo',
            'page_id': env.ref('choreograph_website.bo_homepage'),
            'sequence': 1
        })
