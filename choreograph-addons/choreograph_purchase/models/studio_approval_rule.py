# -*- coding: utf-8 -*-

from ast import literal_eval

from odoo import models, api
from odoo.exceptions import ValidationError, AccessError, UserError


class StudioApprovalRule(models.Model):
    _inherit = 'studio.approval.rule'

    @api.model
    def check_approval(self, model, res_id, method, action_id, force=False):
        if model == 'purchase.order' and method == 'button_confirm' and not force:
            return self.check_ordered_approval(model, res_id, method, action_id)
        res = super(StudioApprovalRule, self).check_approval(model, res_id, method, action_id)
        return res

    @api.model
    def check_ordered_approval(self, model, res_id, method, action_id):
        """
        Same as check_approval(), but create only an entry for the first unapproved rule
        """
        self = self._clean_context()
        if method and action_id:
            raise UserError(_('Approvals can only be done on a method or an action, not both.'))
        record = self.env[model].browse(res_id)
        # we check that the user has write access on the underlying record before doing anything
        # if another type of access is necessary to perform the action, it will be checked
        # there anyway
        record.check_access_rights('write')
        record.check_access_rule('write')
        ruleSudo = self.sudo()
        domain = self._get_rule_domain(model, method, action_id)
        # order by 'exclusive_user' so that restrictive rules are approved first
        rules_data = ruleSudo.search_read(
            domain=domain,
            fields=['group_id', 'message', 'exclusive_user', 'domain', 'can_validate'],
            order='exclusive_user desc, id asc'
        )
        applicable_rule_ids = list()
        for rule in rules_data:
            rule_domain = rule.get('domain') and literal_eval(rule['domain'])
            if not rule_domain or record.filtered_domain(rule_domain):
                applicable_rule_ids.append(rule['id'])
        rules_data = list(filter(lambda r: r['id'] in applicable_rule_ids, rules_data))
        if not rules_data:
            return {'approved': True, 'rules': [], 'entries': []}
        entries_data = self.env['studio.approval.entry'].sudo().search_read(
            domain=[('model', '=', model), ('res_id', '=', res_id), ('rule_id', 'in', applicable_rule_ids)],
            fields=['approved', 'rule_id', 'user_id'])
        entries_by_rule = dict.fromkeys(applicable_rule_ids, False)
        first_non_approved_rule = 0
        for rule_id in entries_by_rule:
            if first_non_approved_rule:
                break
            candidate_entry = list(filter(lambda e: e['rule_id'][0] == rule_id, entries_data))
            candidate_entry = candidate_entry and candidate_entry[0]
            if not candidate_entry:
                first_non_approved_rule = rule_id
                try:
                    new_entry = self.browse(rule_id)._set_approval(res_id, True)
                    entries_data.append({
                        'id': new_entry.id,
                        'approved': True,
                        'rule_id': [rule_id, False],
                        'user_id': self.env.user.name_get()[0]
                    })
                    entries_by_rule[rule_id] = True
                except UserError:
                    self.browse(rule_id)._create_request(res_id)
                    pass
            else:
                entries_by_rule[rule_id] = candidate_entry['approved']

        non_approved_rules = list(filter(lambda e: e['id'] not in list(map(lambda x: x['rule_id'][0], entries_data)), rules_data))
        return {
            'approved': all(entries_by_rule.values()),
            'rules': [non_approved_rules[0]] if non_approved_rules else rules_data,
            'entries': entries_data,
        }
