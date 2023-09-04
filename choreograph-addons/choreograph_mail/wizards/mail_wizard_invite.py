# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Invite(models.TransientModel):
    """ Wizard to invite partners (or channels) and make them followers. """
    _inherit = 'mail.wizard.invite'

    def add_followers(self):
        return super(Invite, self.with_context(manual_follower_add=True)).add_followers()
