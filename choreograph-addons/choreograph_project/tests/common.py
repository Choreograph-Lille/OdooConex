# -*- encoding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.addons.choreograph_contact.tests.common import TestRoleCommon


class TestProjectCommon(TestRoleCommon):
    """Setup with project test configuration."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
