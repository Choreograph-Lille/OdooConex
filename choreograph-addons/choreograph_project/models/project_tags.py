# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.osv import expression


class ProjectTags(models.Model):
    _inherit = "project.tags"

    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        ids = []
        if not (name == '' and operator in ('like', 'ilike')):
            args += [('name', operator, name)]
        if self.env.context.get('project_id'):
            # optimisation for large projects, we look first for tags present on the last 1000 tasks of said project.
            # when not enough results are found, we complete them with a fallback on a regular search
            self.env.cr.execute("""
                    SELECT DISTINCT project_tasks_tags.id
                    FROM (
                        SELECT rel.project_tags_id AS id
                        FROM project_tags_project_task_rel AS rel
                        JOIN project_task AS task
                            ON task.id=rel.project_task_id
                            AND task.project_id=%(project_id)s
                        ORDER BY task.id DESC
                        LIMIT 1000
                    ) AS project_tasks_tags
                """, {'project_id': self.env.context['project_id']})
            project_tasks_tags_domain = [('id', 'in', [row[0] for row in self.env.cr.fetchall()])]
            # we apply the args and limit to the ids we've already found
            ids += self.env['project.tags'].search(expression.AND([args, project_tasks_tags_domain]), limit=limit).ids
        if not limit or limit and len(ids) < limit:
            limit = limit and limit - len(ids)
            ids += self.env['project.tags'].search(expression.AND([args, [('id', 'not in', ids)]]), limit=limit).ids
        return ids
