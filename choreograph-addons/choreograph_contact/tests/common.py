# -*- encoding: utf-8 -*-

from odoo.tests.common import TransactionCase


class TestRoleCommon(TransactionCase):
    """Setup with role test configuration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create role
        cls.role = cls.env['choreograph.role'].create({
            'name': 'Role test',
        })

        # create user client
        cls.client = cls.env['res.users'].create({
            'name': 'Client test',
            'login': 'cltest@test.com',
        })

        # create user worker
        cls.worker = cls.env['res.users'].create({
            'name': 'Worker test',
            'login': 'clwroker@test.com',
        })
