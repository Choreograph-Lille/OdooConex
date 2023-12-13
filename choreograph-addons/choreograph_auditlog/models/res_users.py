from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_roles = fields.Char(compute='compute_user_rules', store=True)

    @api.depends('groups_id')
    def compute_user_rules(self):
        for rec in self:
            group_roles = self.env['res.users.role'].search([]).mapped('group_id')
            rec.user_roles = ','.join(rec.groups_id.filtered(lambda group: group.id in group_roles.ids).mapped('name'))
