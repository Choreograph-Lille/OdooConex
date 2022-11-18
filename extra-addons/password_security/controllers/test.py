def onchange_role_id(self):
    for rec in self:
        if rec.role_id and rec.project_id.partner_id:
            partner_role = rec.project_id.partner_id.role_ids.filtered(lambda r: r.role_id.id == rec.role_id.id)
            rec.user_ids = [(6, 0, partner_role and partner_role.mapped('user_ids').ids or [])]
