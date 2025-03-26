# -*- coding: utf-8 -*-

from odoo import api, fields, models


class NeedsBase(models.AbstractModel):
    _name = "needs.base"

    name = fields.Char('Name')
    need_comment = fields.Text('Comment')
    need_type = fields.Selection([
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('phone', 'Phone'),
        ],
        string='Channel type'
    )
    is_display_comment = fields.Boolean('Display Comment')


class MethodologyNeeds(models.Model):
    _name = "needs.needs"
    _inherit = "needs.base"


class NeedsNeeds(models.Model):
    _name = "methodology.needs"
    _inherit = "needs.base"

    order_id = fields.Many2one('sale.order', 'Order')
    needs_id = fields.Many2one('needs.needs', 'Name')
    
    @api.onchange('order_id.needs_id', 'needs_id')
    def _onchange_needs_id(self):
        self.name = self.needs_id.name
        self.need_comment = self.needs_id.need_comment
        self.need_type = self.needs_id.need_type
        self.is_display_comment = self.needs_id.is_display_comment
