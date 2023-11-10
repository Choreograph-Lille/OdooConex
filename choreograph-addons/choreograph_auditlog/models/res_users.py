from odoo import api, models, fields


class ResUsers(models.Model):
    _inherit = 'res.users'

    user_roles = fields.Char(compute='compute_user_rules', store=True)

    @api.depends('role_line_ids')
    def compute_user_rules(self):
        for rec in self:
            rec.user_roles = ', '.join(rec.role_line_ids.mapped('role_id.name'))
