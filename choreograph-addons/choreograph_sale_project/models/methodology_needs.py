# -*- coding: utf-8 -*-

from odoo import api, fields, models


class NeedsBase(models.AbstractModel):
    _name = "needs.base"

    name = fields.Char('Name')
    volume = fields.Text('Volume/Ventilation')
    average_age = fields.Text('Average Age')
    h_f_percentage = fields.Text('% H/F')
    match_rate = fields.Text('Match Rate')
    other_chanel_potential = fields.Selection([
            ('email', 'Email'),
            ('sms', 'SMS'),
            ('phone', 'Phone'),
        ],
        string='Other Channel Potential'
    )
    other = fields.Text('Other')


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
        self.volume = self.needs_id.volume
        self.average_age = self.needs_id.average_age
        self.h_f_percentage = self.needs_id.h_f_percentage
        self.match_rate = self.needs_id.match_rate
        self.other_chanel_potential = self.needs_id.other_chanel_potential
        self.other = self.needs_id.other
