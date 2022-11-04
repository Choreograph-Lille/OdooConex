# -*- encoding: utf-8 -*-

from .common import TestSaleCommon


class TestSaleOrder(TestSaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # create project model
        cls.project = cls.env['project.project'].create({
            'name': 'Test project model'
        })

        # create task for the project model
        cls.task = cls.env['project.task'].create({
            'name': 'Test task',
            'project_id': cls.project.id,
        })

    def test_sale_order_project_model(self):
        """
        Test create project from order's operation type field
        :return:
        """
        self.sale_order.operation_type = self.project.id
        self.sale_order.action_confirm()

        # test if project number == 1
        self.assertEqual(1, self.sale_order.project_count)

        # test if task number = 2: one from project model and one from article1
        self.assertEqual(2, self.sale_order.tasks_count)
