from .project_project import TYPE_OF_PROJECT, filter_by_type_of_project
from odoo import api, fields, models, _

TASK_NUMBER = [(str(n), str(n)) for n in range(5, 100, 5)]


class ProjectTask(models.Model):
    _inherit = 'project.task'

    role_id = fields.Many2one('res.role', 'Role')
    task_number = fields.Selection(TASK_NUMBER)
    type_of_project = fields.Selection(
        TYPE_OF_PROJECT, default='standard', required=True, compute='_compute_type_of_project', store=True,
        readonly=False)

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
        for rec in self:
            task_stage_id = self.env['project.task.type'].search([('stage_number', '=', number)], limit=1)
            if task_stage_id:
                rec.write({'stage_id': task_stage_id.id})

    @api.model
    def get_operation_project_task_type(self):
        return self.env['project.task.type'].search([('type_of_project', '=', 'operation')])

    @api.model_create_multi
    def create(self, val_list):
        res = self.env[self._name]
        for values in val_list:
            if self._context.get('is_operation_generation'):
                if values.get('task_number', False) == '20' and values.get('project_id', False):
                    project_id = self.env['project.project'].browse(values['project_id']).exists()
                    if project_id:
                        values['name'] = project_id.name.replace(' (TEMPLATE)', '').replace(' (COPY)', '')
                values.update({
                    'stage_id': self.env.ref('choreograph_project.project_task_type_draft').id,
                })
            task = super().create(values)
            task._send_task_notification()
            res |= task
            res.insert_operation_followers()
        return res
    
    def _send_task_notification(self):
        if self.user_ids:
            task_url = f"{self.get_base_url()}/web#id={self.id}&model=project.task&view_type=form"
            users_with_email_notification = self.user_ids.filtered(lambda u: u.notification_type == 'email')
            lang = self.env.user.lang
            if users_with_email_notification:
                mail_template = self.env.ref('choreograph_project.task_notification_template')
                context = {
                    'partner_to':','.join([str(user_id.partner_id.id) for user_id in users_with_email_notification]),
                    'task_url': task_url,
                    'task_name': self.name,
                    'lang':lang
                }
                self.env['mail.thread'].with_context(context).message_post_with_template(
                    mail_template.id, message_type='comment', composition_mode='comment'
                )
            users_with_odoo_notification = self.user_ids.filtered(lambda u: u.notification_type == 'inbox')
            if users_with_odoo_notification:
                partner_ids = users_with_odoo_notification.partner_id.ids
                channel = self.env['mail.channel'].create({
                    'name': self.name,
                    'channel_partner_ids': [(4, partner_id) for partner_id in partner_ids],
                })
                channel.with_user(self.env.user).message_notify(
                    body=_("You are assigned to the task %(task_name)s", task_name = self.name),
                    message_type ='user_notification',
                    partner_ids = partner_ids,
                ) 

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        message = super(ProjectTask, self).message_post(**kwargs)
        no_tracking_subtypes = self.env.ref(
                'project.mt_task_stage') | self.env.ref('project.mt_task_new')
        if self.project_id.type_of_project == 'operation' and message.subtype_id not in no_tracking_subtypes:
            message.copy({'res_id': self.project_id.id, 'model': 'project.project'})
        return message

    def write(self, values):
        res = super().write(values)
        if 'user_ids' in values:
            self.insert_operation_followers()
        return res

    def insert_operation_followers(self):
        for rec in self:
            if rec.type_of_project == 'operation':
                self.env['mail.followers']._insert_followers(
                    'project.project', rec.project_id.ids, rec.user_ids.partner_id.ids)

    @api.model
    def _task_message_auto_subscribe_notify(self, users_per_task):
        """
            disable task assignation
        """
        return

    def _populate_missing_personal_stages(self):
        # HT02429: remove functionality for operations because creating unwanted task types
        tasks = self.filtered(lambda task: task.type_of_project != 'operation')
        super(ProjectTask, tasks)._populate_missing_personal_stages()
