# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    operation_type = fields.Many2one('project.project', string='Operation type', domain=[('is_template', '=', True)])

    class SaleOrder(models.Model):
        _inherit = 'sale.order'

        def _create_project_from_template(self, values, template):
            values['name'] = "%s - %s" % (values['name'], template.name)
            # The no_create_folder context key is used in documents_project
            project = template.with_context(no_create_folder=True).copy(values)
            project.tasks.write({
                'sale_order_id': self.id,
                'partner_id': self.partner_id.id,
                'email_from': self.partner_id.email,
            })
            # duplicating a project doesn't set the SO on sub-tasks
            project.tasks.filtered('parent_id').write({
                'sale_order_id': self.id,
            })
            self.sudo().write({
                'project_id': project.id,
            })
            self.order_line.filtered(lambda sol: sol.is_service and sol.product_id.service_tracking in ['project_only', 'task_in_project']).write({
                'project_id': project.id,
            })

        def _action_confirm(self):
            """ Generate project if operation_type is not False. """
            self.ensure_one()
            if self.operation_type:
                values = self._create_project_prepare_values()
                if len(self.company_id) == 1:
                    # All orders are in the same company
                    self.sudo().with_company(self.company_id)._create_project_from_template(values, self.operation_type)
                else:
                    # Orders from different companies are confirmed together
                    for order in self:
                        order.sudo().with_company(order.company_id)._create_project_from_template(values, self.operation_type)
            return super()._action_confirm()

        def _create_project_prepare_values(self):
            """Generate project values"""
            account = self.analytic_account_id
            if not account:
                service_products = self.order_line.product_id.filtered(
                    lambda p: p.type == 'service' and p.default_code)
                default_code = service_products.default_code if len(service_products) == 1 else None
                self.sudo()._create_analytic_account(prefix=default_code)
                account = self.analytic_account_id

            # create the project or duplicate one
            return {
                'name': '%s - %s' % (self.client_order_ref,
                                     self.name) if self.client_order_ref else self.name,
                'analytic_account_id': account.id,
                'partner_id': self.partner_id.id,
                'sale_order_id': self.id,
                'active': True,
                'company_id': self.company_id.id,
                'allow_billable': True,
            }