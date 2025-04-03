# -*- coding: utf-8 -*-

from odoo import _, api, fields, models

import re

from odoo.exceptions import ValidationError

TYPE_SELECTION = [
    ('score', 'SCORE'),
    ('selection', 'SELECTION'),
]


def count_word(list_of_strings, word):
    """
    Count the frequency of words in a list of strings.
    :param list_of_strings: {list} list of strings to check
    :param word: {str} word to count
    :return: the number of times each word appears in the list
    """
    target_lower = word.lower()
    return sum(1 for text in list_of_strings
               for word in re.findall(r'\b\w+\b', text.lower())
               if word == target_lower)


class MethodologySelection(models.AbstractModel):
    _name = "methodology.selection"

    name = fields.Char('Name', translate=True)
    type = fields.Selection(TYPE_SELECTION, string='Type')
    display_textarea = fields.Boolean('Display Textarea ?')


class MethodologyScoreTarget(models.Model):
    _name = "methodology.score.target"
    _inherit = "methodology.selection"
    _description = "Methodology Score Target"


class MethodologyTargetRecence(models.Model):
    _name = "methodology.target.recence"
    _inherit = "methodology.selection"
    _description = "Methodology Target Recence"


class MethodologyTargetFilter(models.Model):
    _name = "methodology.target.filter"
    _inherit = "methodology.selection"
    _description = "Methodology Target Filter"


class MethodologyCustomerFilter(models.Model):
    _name = "methodology.customer.filter"
    _inherit = "methodology.selection"
    _description = "Methodology Customer Filter"


class MethodologyName(models.Model):
    _name = "methodology.name"
    _inherit = "methodology.selection"
    _description = "Methodology Name"

    target_id = fields.Many2one('methodology.score.target', 'Target')


class MethodologyMethodology(models.Model):
    _name = "methodology.methodology"
    _description = "Methodology"
    _translate = True

    @api.model
    def default_get(self, fields):
        res = super(MethodologyMethodology, self).default_get(fields)
        order_id = self._context.get('default_order_id') or self._context.get('params', {}).get('id', False)
        if order_id:
            res['order_id'] = order_id
            section_type = res.get('type', False)
            last_section = self.get_sections(order_id)
            section_owner = last_section[0].name if last_section else False
            if section_type:
                name = section_type + ' ' + str(self.check_existing_section(section_type, order_id) + 1)
                res['name'] = name.upper()
            if section_owner:
                res['section_owner'] = section_owner
                display_type = res.get('display_type', False)
                if not display_type:
                    type = section_owner.lower().split(' ')[0]
                    # res['type'] = type
                    if type == 'score':
                        target_recence = 'choreograph_sale_project.target_0_12'
                    else:
                        target_recence = 'choreograph_sale_project.selection_default'
                    res['target_recence_id'] = self.env.ref(target_recence)
        return res

    name = fields.Char('Name', readonly=True)
    type = fields.Selection(TYPE_SELECTION, 'Type')
    methodology_name_id = fields.Many2one('methodology.name', 'Methodology name')
    target_id = fields.Many2one('methodology.score.target', 'Target')
    target_textarea_show = fields.Boolean(string='Display textarea ?')
    target_textarea = fields.Text('Textarea')
    order_id = fields.Many2one('sale.order', 'Order')
    section_owner = fields.Char('Section Owner')
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
        ],
        default=False
    )  # Juste for data display
    target_recence_id = fields.Many2one('methodology.target.recence', string='Target Recence/Selection')
    target_recence_textarea_show = fields.Boolean(related='target_recence_id.display_textarea')
    recence_textarea = fields.Text('Textarea')
    target_filter_id = fields.Many2one('methodology.target.filter', string='Target Filter')
    target_filter_textarea_show = fields.Boolean(related='target_filter_id.display_textarea')
    filter_textarea = fields.Text('Textarea')
    customer_filter_id = fields.Many2one('methodology.customer.filter', string='Customer Filter Type')
    customer_filter_textarea_show = fields.Boolean(related='customer_filter_id.display_textarea')
    customer_filter_textarea = fields.Text('Textarea')

    @api.model_create_multi
    def create(self, vals_list):
        sequence = {
            'score': 0,
            'selection': 0,
        }
        order_id = vals_list[0].get('order_id')
        last_section = self.get_sections(order_id)
        section_owner = last_section[0].name if last_section else ''
        for vals in vals_list:
            section_type = vals.get('type', '')
            if section_type in ('score', 'selection'):
                sequence.update({section_type: self.check_existing_section(section_type, order_id) + 1})
                section_owner = section_type + ' ' + str(sequence.get(section_type))
                vals.update({ 'name': section_owner.upper() })
            vals.update({
                'section_owner': section_owner,
                'type': section_owner.lower().split(' ')[0],
            })

        return super(MethodologyMethodology, self).create(vals_list)

    def check_existing_section(self, word, order_id):
        existing_section_line = self.get_sections(order_id)
        list_name = existing_section_line.mapped('name')
        return count_word(list_name, word)

    def get_sections(self, order_id):
        return self.search([('display_type', '=', 'line_section'), ('order_id', '=', order_id)], order='id desc')

    @api.onchange('methodology_name_id')
    def _onchange_methodology_name_id(self):
        if self.methodology_name_id:
            target_id = self.methodology_name_id.target_id
            if target_id:
                self.target_id = target_id

    @api.onchange('target_id', 'methodology_name_id')
    def _onchange_target_id(self):
        meillail_methodo_id = self.env.ref('choreograph_sale_project.meillaill')
        if self.methodology_name_id and self.methodology_name_id.id == meillail_methodo_id.id:
            self.target_id = False
        if self.target_id:
            self.target_textarea_show = self.target_id.display_textarea
        elif self.methodology_name_id:
            self.target_textarea_show = True
        else:
            self.target_textarea_show = False

    @api.onchange('section_owner')
    def _onchange_section_owner(self):
        if self.section_owner:
            section_type = self.section_owner.lower().split(' ')[0]
            return {'domain': {'target_recence_id': [('type', '=', section_type)]}}

