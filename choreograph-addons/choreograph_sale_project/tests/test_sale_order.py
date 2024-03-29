# -*- encoding: utf-8 -*-

from .common import TestSaleCommon


class TestSaleOrder(TestSaleCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_sale_order_project_model(self):
        """
        Test create project from order's button
        :return:
        """
        self.sale_order.action_confirm()
        # should not generate project/task but status change
        # test if project number = 0
        self.assertEqual(0, self.sale_order.project_count)
        self.assertEqual('sale', self.sale_order.state)

        self.sale_order.action_generate_operation()
        # test if project number == 1
        self.assertEqual(1, self.sale_order.project_count)

        # test if task number = 1: from article1
        self.assertEqual(1, self.sale_order.tasks_count)

        # create condition/exclusion
        self.cond_exc = self.env['operation.condition'].create({
            'operation_type': 'condition',
            'condition_subtype': 'client_file',
            'note': 'NOTE TEST',
            'order_id': self.sale_order.id,
            'file_name': 'File Name',
        })

        self.cond_exc._compute_subtype()
        self.cond_exc._compute_task_number()

        # check if the button is shown
        self.assertEqual(1, self.sale_order.new_condition_count)
        self.assertEqual(1, self.sale_order.project_count)

        # generate the task
        self.sale_order.action_create_task_from_condition()
        self.sale_order._compute_tasks_ids()

        # test if task number = 2: from article1 and from the condition/exclusion
        self.assertEqual(2, self.sale_order.tasks_count)

        # check if the button is hidden
        self.sale_order._compute_new_condition_count()
        self.assertEqual(0, self.sale_order.new_condition_count)
