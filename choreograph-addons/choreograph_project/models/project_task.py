from .project_project import TYPE_OF_PROJECT, filter_by_type_of_project
from odoo import api, fields, models

TASK_NUMBER = [(str(n), str(n)) for n in range(5, 100, 5)]


class ProjectTask(models.Model):
    _inherit = 'project.task'

    role_id = fields.Many2one('res.role', 'Role')
    task_number = fields.Selection(TASK_NUMBER)
    type_of_project = fields.Selection(
        TYPE_OF_PROJECT, default='standard', required=True, compute='_compute_type_of_project', store=True, readonly=False)

    @api.onchange('role_id')
    def onchange_role_id(self):
        partner_role = self.partner_id.role_ids.filtered(lambda r: r.role_id.id == self.role_id.id)
        self.user_ids = [
            (6, 0, self.role_id and self.partner_id and partner_role and partner_role[0].user_ids.ids or [])]

    @api.depends('project_id')
    def _compute_type_of_project(self):
        for rec in self:
            rec.type_of_project = rec.project_id.type_of_project if rec.project_id else 'standard'

    @api.model
    @filter_by_type_of_project
    def _read_group_stage_ids(self, stages, domain, order):
        return super()._read_group_stage_ids(stages, domain, order)

    @api.model
    @filter_by_type_of_project
    def _read_group_personal_stage_type_ids(self, stages, domain, order):
        return super()._read_group_personal_stage_type_ids(stages, domain, order)

    def update_task_stage(self, number):
        task_stage_id = self.env['project.task.type'].search([('stage_number', '=', number)], limit=1)
        if task_stage_id:
            self.write({'stage_id': task_stage_id.id})

    @api.model
    def get_operation_project_task_type(self):
        return self.env['project.task.type'].search([('type_of_project', '=', 'operation')])

    @api.model
    def create(self, values):
        if self._context.get('is_operation_generation'):
            if values.get('task_number', False) == '20' and values.get('project_id', False):
                project_id = self.env['project.project'].browse(values['project_id']).exists()
                if project_id:
                    values['name'] = project_id.name.replace(' (TEMPLATE)', '').replace(' (COPY)', '')
            values.update({
                'stage_id': self.env.ref('choreograph_project.project_task_type_draft').id,
            })
        return super().create(values)

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        message = super(ProjectTask, self).message_post(**kwargs)
        if self.project_id.type_of_project == 'operation':
            message.copy({'res_id': self.project_id.id, 'model': 'project.project'})
        return message
