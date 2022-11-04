# -*- encoding: utf-8 -*-

from .common import TestRoleCommon


class TestResPartner(TestRoleCommon):

    def test_res_partner(self):
        """
        Test adding roles in partner
        :return:
        """
        self.client.partner_id.write({
            'role_ids': [(0, 0, {
                'partner_id': self.client.partner_id.id,
                'role_id': self.role.id,
                'user_ids': [(4, self.worker.id)]
            })],
        })
