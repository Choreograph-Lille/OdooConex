from odoo import models


class MailFollowers(models.Model):
    _inherit = 'mail.followers'

    def _get_recipient_data(self, records, message_type, subtype_id, pids=None):
        doc_infos = super()._get_recipient_data(records, message_type, subtype_id, pids=pids)
        if records._name in ['project.project', 'project.task'] and message_type != 'comment':
            return self._remoce_cp_from_recipients(records, doc_infos)
        return doc_infos

    def _remoce_cp_from_recipients(self, records, doc_infos):
        """
        Remove CP partners from recipients by making active = False
        :param records:
        :param doc_infos:
        :return:
        """
        cp_ids = self.get_cp_ids(records)
        for pid, pdata in doc_infos.items():
            for res_id, res_data in pdata.items():
                if res_id in cp_ids:
                    res_data['active'] = False
        return doc_infos

    def get_cp_ids(self, records):
        """
        Get all CP role from partner_id
        :param records:
        :return:
        """
        cp_ids = []
        for rec in records:
            cp_ids.extend(rec.partner_id.role_ids.filtered(lambda role: role.role_id.id == self.env.ref('choreograph_contact.res_role_cp').id).user_ids.partner_id.ids)
        return cp_ids
