# -*- coding: utf-8 -*-

from odoo import fields, models


class MethodologyNeeds(models.Model):
    _name = "methodology.needs"

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
    order_id = fields.Many2one('sale.order', 'Order')
