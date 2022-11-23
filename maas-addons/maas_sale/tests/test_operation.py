# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import fields
from odoo.tests.common import TransactionCase

logger = logging.getLogger(__name__)


class OperationTest(TransactionCase):

    def setUp(self):
        super(OperationTest, self).setUp()
        self.partner = self.env.ref('maas_base.res_partner_arkeup')
        self.company = self.env.ref('base.main_company')

    def test_create_operation_010(self):
        """
            1. Create an operation
            2. Check it's state as draft
        """
        vals = {
            'name': 'My First Operation',
            'partner_id': self.partner.id,
            'company_id': self.company.id,
            'date': fields.Date.today(),
            'qty_extracted': 200000,
            'population_scored_desc': 'Test',
            'searched_profile_desc': 'Test',
            'type': 'prm',
        }
        campaign = self.env['sale.campaign'].create({'name': 'Campaign test'})
        vals.update({'campaign_id': campaign.id})
        operation = self.env['sale.operation'].create(vals)
        self.assertEqual(operation.state, 'in_progress', 'The state of your operation is not correct!')
