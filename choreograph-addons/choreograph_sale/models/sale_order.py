# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

OPERATION_CONDITION_TYPE = {
    'file_processing': 'File Condition',
    'maj_condition': 'MAJ Condition',
    'sale_order': 'Sale Order Condition',
    'exclusion': 'Exclusion',
    'exclusion_so': 'Sale Order Exclusion',
    'comment': 'Comment',
}
OPERATION_TYPE = {
    'condition': 'Condition',
    'exclusion': 'Exclusion',
}
REQUIRED_TASK_NUMBER = {
    'potential_return': '25',
    'study_delivery': '30',
    'presentation': '35',
}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    show_operation_generation_button = fields.Boolean(default=True)
    operation_condition_ids = fields.One2many('operation.condition', 'order_id')
    new_condition_count = fields.Integer(compute='_compute_new_condition_count')
    catalogue_ids = fields.Many2many('res.partner.catalogue', 'sale_order_partner_catalogue_rel', 'sale_order_id', 'catalogue_id', 'Catalogues')
    prefulfill_study = fields.Boolean('Pre-fulfill study')
    related_base = fields.Many2one('retribution.base', string='Related base')
    data_conservation = fields.Char('Data conservation')
    receiver = fields.Char('Receiver')
    send_with = fields.Char('Send with')
    operation_type_id = fields.Many2one('project.project', string='Operation type')
    total_retribution = fields.Float(compute="_compute_total_retribution")

    po_number = fields.Char('PO Number')
    campaign_name = fields.Char('Campaign Name')
    is_info_validated = fields.Boolean('Infos Validated')
    routing_date = fields.Date('Routing Date')
    routing_end_date = fields.Date('Routing End Date')
    desired_finished_volume = fields.Char('Desired Finished Volume')
    volume_detail = fields.Text('Volume Detail')
    sender = fields.Char('Sender')

    reception_date = fields.Date('Reception Date')
    reception_location = fields.Char('Where to find ?')
    personalization = fields.Boolean('Personalization')
    comment = fields.Text('Comment')

    bat_from = fields.Char('From')
    bat_internal_client = fields.Char('BAT Internal/Client')
    bat_comment = fields.Text('BAT Comment')

    witness_file_name = fields.Char('File Name')
    witness_comment = fields.Text('Witness Comment')

    @api.depends('order_line')
    def _compute_total_retribution(self):
        for rec in self:
            rec.total_retribution = sum(rec.order_line.mapped('retribution_cost'))

    def get_operation_product(self):
        return self.order_line.filtered(lambda l: l.operation_template_id)

    def action_generate_operation(self):
        # check for tasks in operation template
        line_with_project = self.get_operation_product()
        if line_with_project:
            tasks = line_with_project[0].operation_template_id.task_ids.mapped('task_number')
            if any([task not in tasks for task in REQUIRED_TASK_NUMBER.values()]):
                raise ValidationError(_('The operation template must have the following task number: {0}, {1}, {2}').format(REQUIRED_TASK_NUMBER['potential_return'], REQUIRED_TASK_NUMBER['study_delivery'], REQUIRED_TASK_NUMBER['presentation']))
        self.order_line.sudo().with_company(self.company_id).with_context(is_operation_generation=True)._timesheet_service_generation()
        self.show_operation_generation_button = False

        for task in self.tasks_ids.filtered(lambda t: t.task_number in REQUIRED_TASK_NUMBER.values()):
            task.active = False

    def action_create_task_from_condition(self):
        for rec in self:
            for condition in self.operation_condition_ids.filtered(lambda c: not c.is_task_created and c.type != 'comment'):
                vals = {
                    'name': rec.name + '/' + OPERATION_TYPE[condition.operation_type] + '/' + OPERATION_CONDITION_TYPE[condition.type],
                    'partner_id': rec.partner_id.id,
                    'email_from': rec.partner_id.email,
                    'description': condition.note,
                    'sale_order_id': rec.id,
                    'user_ids': False,
                }
                vals['name'] += condition.subtype_id.name if condition.subtype_id else ''
                rec.project_ids.task_ids = [(0, 0, vals)]
                condition.is_task_created = True

    def _compute_new_condition_count(self):
        self.new_condition_count = len(self.operation_condition_ids.filtered(
            lambda c: not c.is_task_created and c.type != 'comment'))

    def _reset_show_operation_generation_button(self, vals):
        vals['show_operation_generation_button'] = True
        return vals

    @api.model
    def create(self, vals):
        vals = self._reset_show_operation_generation_button(vals)
        return super(SaleOrder, self).create(vals)
