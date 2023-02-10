from odoo import api, models


class ProjectUpdate(models.Model):
    _inherit = 'project.update'

    @api.model
    def js_redelivery(self, active_id, type_redelivery):
        project_id = self.env['project.project'].browse(active_id).exists()
        if project_id and type_redelivery == 'studies':
            project_id.js_redelivery_studies()
        if project_id and type_redelivery == 'prod':
            project_id.js_redelivery_prod()
