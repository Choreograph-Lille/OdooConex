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
    is_required_target = fields.Boolean('Is required target ?')


class MethodologyMethodology(models.Model):
    _name = "methodology.methodology"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Methodology"
    _translate = True

    name = fields.Char('Name Type', tracking=True)
    type = fields.Selection(TYPE_SELECTION, 'Type', tracking=True)
    methodology_name_id = fields.Many2one('methodology.name', 'Methodology name', tracking=True)
    is_required_target = fields.Boolean('Is required target ?',compute='_compute_is_required_target')
    target_id = fields.Many2one('methodology.score.target', 'Target', tracking=True)
    target_textarea_show = fields.Boolean(string='Display textarea ?', tracking=True)
    target_textarea = fields.Text('Textarea', tracking=True)
    order_id = fields.Many2one('sale.order', 'Order', tracking=True)
    project_id = fields.Many2one('project.project', 'Project', tracking=True)
    section_owner = fields.Char('Section Owner')
    sequence = fields.Integer('Sequence')
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
        ],
        default=False
    )  # Juste for data display
    target_recence_id = fields.Many2one('methodology.target.recence', string='Target Recence/Selection', tracking=True)
    target_recence_textarea_show = fields.Boolean(related='target_recence_id.display_textarea', tracking=True)
    recence_textarea = fields.Text('Textarea', tracking=True)
    target_filter_id = fields.Many2one('methodology.target.filter', string='Target Filter', tracking=True)
    target_filter_textarea_show = fields.Boolean(related='target_filter_id.display_textarea', tracking=True)
    filter_textarea = fields.Text('Textarea', tracking=True)
    customer_filter = fields.Text('Custom Filter', compute='compute_customer_filter')

    methodology_filter_ids = fields.One2many('methodology.methodology.filter', 'methodology_id', string='Methodology Filters')


    @api.model_create_multi
    def create(self, vals_list):
        order_id = self.env['sale.order'].browse(vals_list[0].get('order_id')) 
        score_count = order_id.score_count
        selection_count = order_id.selection_count
        for vals in vals_list:
            section_type = vals.get('type', '')
            if section_type in ('score', 'selection'):
                if section_type == 'score':
                    score_count += 1
                else:
                    selection_count += 1
                name = section_type + ' ' + str(score_count) if section_type == 'score' else section_type + ' ' + str(selection_count)
                vals.update({ 'name': name.upper() })

        return super(MethodologyMethodology, self).create(vals_list)

    def check_existing_section(self, word, order_id):
        existing_section_line = self.get_sections(order_id)
        list_name = existing_section_line.mapped('name')
        return count_word(list_name, word)

    def get_sections(self, order_id):
        return self.search([('display_type', '=', 'line_section'), ('order_id', '=', order_id)], order='id desc')

    @api.depends('methodology_name_id', 'type')
    def _compute_is_required_target(self):
        for record in self:
            if record.methodology_name_id:
                record.is_required_target = record.methodology_name_id.is_required_target
            else:
                record.is_required_target = False

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
            if not self._context.get('default_display_type', False):
                self.type = section_type
            return {'domain': {'target_recence_id': [('type', '=', section_type)]}}
    
    def _reset_all_value(self):
        self.target_textarea = False
        self.recence_textarea = False
        self.filter_textarea = False   

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'score':
            self.target_recence_id = self.env.ref('choreograph_sale_project.target_0_12', raise_if_not_found=False).id
            self.name = "SCORE %s" % (str(len(self.order_id.methodology_ids.filtered(lambda m: m.type == 'score'))))
        else:
            self.target_recence_id = self.env.ref('choreograph_sale_project.selection_default', raise_if_not_found=False).id
            self.name = "SELECTION %s" % (str(len(self.order_id.methodology_ids.filtered(lambda m: m.type == 'selection'))))
        
    
    @api.onchange('target_id')
    def _reset_target_textarea(self):
        self.target_textarea = False

    @api.onchange('target_recence_id')
    def _reset_target_recence(self):
        self.recence_textarea = False

    @api.onchange('target_filter_id')
    def _reset_filter_textarea(self):
        self.filter_textarea = False
    
    @api.depends('methodology_filter_ids')
    def compute_customer_filter(self):
        for record in self:
            filters = []
            customer_filter_ids = record.methodology_filter_ids.customer_filter_ids
            if customer_filter_ids:
                filters = [
                    f"{cf.customer_filter_id.name}             {cf.customer_filter_textarea or ''}" for cf in customer_filter_ids
                ]
            record.customer_filter = '\n'.join(filters)
    
    def action_show_filters(self):
        self.ensure_one()

        filter_rec = self.env['methodology.methodology.filter'].search(
            [('methodology_id', '=', self.id)],
            limit=1
        )

        if not filter_rec:
            filter_rec = self.env['methodology.methodology.filter'].create({
                'methodology_id': self.id,
            })

        return {
            'name': _('Methodology Filters'),
            'type': 'ir.actions.act_window',
            'res_model': 'methodology.methodology.filter',
            'view_mode': 'form',
            'view_id': self.env.ref(
                'choreograph_sale_project.methodology_methodology_filter_view_form'
            ).id,
            'res_id': filter_rec.id,  
            'target': 'new',
        }

class MethodologyMethodologyFilter(models.Model):
    _name = "methodology.methodology.filter"
    _description = "Methodology Methodology Filter"

    methodology_id = fields.Many2one('methodology.methodology', 'Methodology')
    customer_filter_ids = fields.One2many('methodology.methodology.custom.filter', 'methodology_filter_id', string='Customer Filters')

class MethodologyMethodologyCustomFilter(models.Model):
    _name = "methodology.methodology.custom.filter"
    _description = "Methodology Methodology Custom Filter"

    methodology_filter_id = fields.Many2one('methodology.methodology.filter', 'Methodology Filter')
    customer_filter_id = fields.Many2one('methodology.customer.filter', string='Customer Filter Type')
    customer_filter_textarea_show = fields.Boolean(related='customer_filter_id.display_textarea', store=True)
    customer_filter_textarea = fields.Text('Textarea')

    @api.onchange('customer_filter_id')
    def _onchange_customer_filter_id(self):
        if self.customer_filter_id:
            self.customer_filter_textarea = False