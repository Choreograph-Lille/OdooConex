# -*- coding: utf-8 -*-

from odoo import models, fields, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    role_ids = fields.One2many("res.partner.role", "partner_id", "Roles")
    country_base = fields.Selection([("uk", "UK"), ("fr", "FR")], "Country Base", default="fr", tracking=True)
    category_name = fields.Char("Category Name", tracking=True)
    last_revival_date = fields.Date("Last Revival Date", tracking=True)
    last_transaction_date = fields.Date("Last Transaction Date", tracking=True)
    data_destruction_date = fields.Date("Data Destruction Date", tracking=True)
    contract_update_date = fields.Date("Contract Update Date", tracking=True)
    rescission_date = fields.Date("Rescission Date", tracking=True)
    base_entry_date = fields.Date("Base Entry Date", tracking=True)
    last_conexup_date = fields.Date("Last Conexup Date", tracking=True)
    last_receipt_date = fields.Date("Last Receipt Date", tracking=True)
    first_contract_date = fields.Date("First Contract Date", tracking=True)
    is_dpo = fields.Boolean("DPO", tracking=True)
    update_frequency = fields.Char("Update Frequency", tracking=True)
    catalogue_ids = fields.Many2many("res.partner.catalogue", "res_partner_catalogue_rel",
                                     "partner_id", "catalogue_id", "Catalogues")
    private_title = fields.Boolean("Private Title", tracking=True)
    agency_id = fields.Many2one("res.partner", "Agency", ondelete="restrict", index=True, tracking=True)
    industry_id = fields.Many2one("res.partner.industry", "Activity area", tracking=True)
    function = fields.Char(string="Job Position", tracking=True)

    def write(self, vals):

        catalogues_summary = {}
        categories_summary = {}
        roles_summary = {}

        if "catalogue_ids" in vals:
            catalogues_summary = self._get_current_catalogues()
        if "category_id" in vals:
            categories_summary = self._get_current_categories()
        if "role_ids" in vals:
            roles_summary = self._get_current_roles()

        res = super(ResPartner, self).write(vals)

        if "catalogue_ids" in vals:
            self._post_catalogues_message(catalogues_summary)
        if "category_id" in vals:
            self._post_categories_message(categories_summary)
        if "role_ids" in vals:
            self._post_roles_message(roles_summary)

        return res

    def _get_current_catalogues(self):
        catalogues_summary = {}
        for partner in self:
            for catalog in partner.catalogue_ids:
                catalogues_summary.setdefault(partner.id, []).append(catalog.name)
        return catalogues_summary

    def _get_current_categories(self):
        categories_summary = {}
        for partner in self:
            for category in partner.category_id:
                categories_summary.setdefault(partner.id, []).append(category.name)
        return categories_summary

    def _get_current_roles(self):
        roles_summary = {}
        for partner in self:
            for role in partner.role_ids:
                for user in role.user_ids:
                    roles_summary.setdefault(partner.id, {}).setdefault(role.role_id.name, []).append(user.name)
        return roles_summary

    def _post_catalogues_message(self, catalogues={}):
        for partner in self:
            body = _("""
                <ul>
                    <li><strong>Catalogues: </strong>
                    <ul>
                        <li><strong>Previous values: </strong>%s
                        <li><strong>New values: </strong>%s
                    </ul>
                </ul>
            """) % (catalogues.get(partner.id) or None, partner.catalogue_ids.mapped("name") or None)
            partner.message_post(body=body)
        return True

    def _post_categories_message(self, categories={}):
        for partner in self:
            body = _("""
                <ul>
                    <li><strong>Categories: </strong>
                    <ul>
                        <li><strong>Previous values: </strong>%s
                        <li><strong>New values: </strong>%s
                    </ul>
                </ul>
            """) % (categories.get(partner.id) or None, partner.category_id.mapped("name") or None)
            partner.message_post(body=body)
        return True

    def _post_roles_message(self, roles={}):
        for partner in self:
            body = _("""
                <ul>
                    <li><strong>Roles: </strong>
                    <ul>
                        <li><strong>Previous values: </strong> 
                            <ul>
                                %s
                            </ul>
                        <li><strong>New values: </strong>
                            <ul>
                                %s
                            </ul>
                    </ul>
                </ul>
            """) % (self._manage_previous_role_message_structure(roles.get(partner.id, {})),
                    self._manage_new_role_message_structure(partner.role_ids))
            partner.message_post(body=body)
        return True

    def _manage_previous_role_message_structure(self, roles):
        self.ensure_one()
        body = ""
        for role, users in roles.items():
            body += """
                <li><strong>%s: </strong> %s        
            """ % (role, users)
        return body

    def _manage_new_role_message_structure(self, roles):
        self.ensure_one()
        body = ""
        for role in roles:
            body += """
                <li><strong>%s: </strong> %s            
            """ % (role.role_id.name, role.user_ids.mapped("name"))
        return body
