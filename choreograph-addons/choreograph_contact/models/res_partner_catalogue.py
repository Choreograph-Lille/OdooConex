# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerCatalogue(models.Model):
    _name = 'res.partner.catalogue'
    _description = 'Partner Catalogue'

    name = fields.Char('Name')
    color = fields.Integer('Color', default=1)
    active = fields.Boolean(default=True)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False, access_rights_uid=None):
        if self._context.get('filter_by_partner_catalogue'):
            args += [('id', 'in', self.env['res.partner'].browse(self._context.get('filter_by_partner_catalogue')).catalogue_ids.ids)]
        return super(ResPartnerCatalogue, self)._search(args, offset=offset, limit=limit, order=order,
                                                              count=count,
                                                              access_rights_uid=access_rights_uid)
