# -*- encoding: utf-8 -*-

from .common import TestProjectCommon


class TestProject(TestProjectCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # create project
        cls.project = cls.env['project.project'].create({
            'name': 'Project Test',
            'partner_id': cls.client.partner_id.id,
        })

        # create task
        cls.task = cls.env['project.task'].create({
            'name': 'Project Test',
            'project_id': cls.project.id
        })

    def test_project_task(self):
        """
        Test adding role in task
        :return:
        """

        self.client.partner_id.write({
            'role_ids': [(0, 0, {
                'partner_id': self.client.partner_id.id,
                'role_id': self.role.id,
                'user_ids': [(4, self.worker.id)]
            })],
        })

        self.task.write({
            'role_id': self.role.id
        })
        self.task.onchange_role_id()
        self.assertIn(self.worker.id, self.task.user_ids.ids)
