# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2018 ArkeUp (<http://www.arkeup.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
import json
import os

from odoo import http, modules

from odoo.addons.http_routing.models.ir_http import url_for


class OperationWebsite(http.Controller):

    @staticmethod
    def _get_consumption_data():
        partner = http.request.env.user.partner_id
        subscription = partner.get_active_subscription()
        if not subscription:
            return 0, 0, 0, False
        identifiers = subscription.current_package_id.identifiers
        quantity = subscription.current_cumulative_quantity
        percent = round(quantity * 100.0 / (identifiers or 1), 2)
        unlimited = subscription.current_package_id.unlimited
        return quantity, identifiers, percent, unlimited

    @http.route('/operation/list', auth='user', website=True, csrf=False)
    def index(self, **kwargs):
        quantity, identifiers, percent, unlimited = self._get_consumption_data()
        partner = http.request.env.user.partner_id.get_parent()
        values = {
            'campaign_ids': partner.campaign_ids,
            'total_qty_cumulative': quantity,
            'identifiers': identifiers,
            'percent': percent,
            'url_for': url_for,
            'user': http.request.env.user,
            'unlimited': unlimited
        }
        return http.request.render('maas_website.operation_list', values, True)

    @http.route('/operation/create', auth='user', website=True)
    def create_operation(self):
        quantity, identifiers, percent, unlimited = self._get_consumption_data()
        partner = http.request.env.user.partner_id.get_parent()
        canal = http.request.env.user.get_canal()
        values = {
            'campaign_ids': partner.campaign_ids,
            'total_qty_cumulative': quantity,
            'identifiers': identifiers,
            'percent': percent,
            'url_for': url_for,
            'unlimited': unlimited,
            'canal': canal
        }
        return http.request.render('maas_website.operation_creation', values)

    @http.route('/operation/launch', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def launch_operation(self, **kwargs):
        operation_obj = http.request.env['sale.operation']
        partner = http.request.env.user.partner_id.get_parent()
        canal = kwargs.get('canal')
        canal = canal if canal != 'null' and canal in ('SMS', 'Print', 'Email') else False
        operation = operation_obj.create({'name': kwargs.get('name'),
                                          'is_customer': True,
                                          'partner_id': partner.id,
                                          'campaign_id': kwargs.get('campaign_id', False),
                                          'action_id': kwargs.get('action_id', False),
                                          'searched_profile_desc': kwargs.get('searched_profile_desc'),
                                          'population_scored_desc': kwargs.get('population_scored_desc'),
                                          'population_scored_datafile': base64.encodebytes(
                                              kwargs.get('population_scored_datafile').read()),
                                          'population_scored_filename': kwargs.get(
                                              'population_scored_datafile').filename,
                                          'searched_profile_datafile': base64.encodebytes(
                                              kwargs.get('searched_profile_datafile').read()),
                                          'searched_profile_filename': kwargs.get(
                                              'searched_profile_datafile').filename,
                                          'canal': canal})
        res = {operation.id: {'name': operation.name}}
        return json.dumps(list(res.values()))

    @http.route('/operation/accept', auth='user', methods=['POST'], website=True, csrf=False)
    def accept_operation(self):
        return http.request.redirect('/operation/list')

    @http.route('/operation/modeling', auth='user', methods=['POST'], website=True, csrf=False)
    def modeling_operation(self, **kwargs):
        operation_obj = http.request.env['sale.operation.child']
        package_obj = http.request.env['package.upgrade']
        operation = operation_obj.browse(int(kwargs.get('operation_id')))
        subscription = operation.partner_id.get_active_subscription()
        if not subscription:
            return http.request.redirect('/operation/list')
        if kwargs.get('use_available_identifiers'):
            operation.write({'qty_extracted': subscription.balance})
        else:
            operation.write({'qty_extracted': int(kwargs.get('volume_filled'))})
        if kwargs.get('request_for_validation'):
            operation.request_package_upgrade()
            return http.request.redirect('/operation/list' + '#operation' + str(operation.operation_id.id))
        result = operation.command_ordered()
        if isinstance(result, bool):
            return http.request.redirect('/operation/list')
        wizard = package_obj.with_context(result['context']).create({})
        wizard.button_validate()
        return http.request.redirect('/operation/list' + '#operation' + str(operation.operation_id.id))

    @http.route('/operation/detail/<int:operation_id>', type='http', auth='user', methods=['POST'], website=True,
                csrf=False)
    def detail_operation(self, operation_id):
        operation_obj = http.request.env['sale.operation']
        operation = operation_obj.browse(operation_id)
        res = {operation.id: {'name': operation.name,
                              'searched_profile_desc': operation.searched_profile_desc,
                              'population_scored_desc': operation.population_scored_desc,
                              'searched_profile_count': str(operation.searched_profile_count),
                              'population_scored_count': str(operation.population_scored_count),
                              'campaign_id': operation.campaign_id.name,
                              'action_id': operation.action_id.name}}
        return json.dumps(list(res.values()))

    @http.route('/operation/update/<int:operation_id>/<string:type>/<int:volume>', type='http', auth='user',
                methods=['POST'], website=True,
                csrf=False)
    def update_operation(self, operation_id, type, volume, **kwargs):
        operation_obj = http.request.env['sale.operation']
        operation_child = http.request.env['sale.operation.child']
        operation = operation_obj.browse(operation_id)
        partner = http.request.env.user.partner_id.get_parent()
        subscription = partner.get_active_subscription()
        res = {}
        if not subscription:
            return json.dumps(list({'show_popup': False}))
        vals = dict()
        vals['operation_id'] = operation.id
        vals['type'] = type
        vals['qty_extracted'] = volume

        try:
            result = operation_child.create(vals)
        except Exception as e:
            res = {'operation': {'show_popup': True, 'except': True, 'text': e.args[0]}}
            return json.dumps(list(res.values()))
        if kwargs.get('sens', False) and type == 'initial_command':
            result.operation_id.write({'sens': kwargs['sens']})
        try:
            boolean = result.command_ordered()
            if isinstance(boolean, bool):
                return json.dumps(list({'show_popup': False}))
            res = {result.id: {'id': result.id, 'show_popup': True,
                               'available_identifiers': subscription.balance,
                               'volume_filled': volume, 'difference': subscription.balance - volume,
                               'product_name': boolean['context'].get('product_name'),
                               'except': False, 'text': False}}
        except Exception as e:
            res = {result.id: {'id': result.id, 'show_popup': True, 'except': True, 'text': e.args[0]}}

        return json.dumps(list(res.values()))

    @http.route('/operation/update/campaign_action/<int:operation_id>/<string:type>/<int:value>', type='http',
                auth='user',
                methods=['POST'], website=True, csrf=False)
    def update_campaign_action(self, operation_id, type, value):
        operation_obj = http.request.env['sale.operation']
        action_obj = http.request.env['sale.campaign.action']
        operation = operation_obj.browse(operation_id)
        if type == 'campaign':
            operation.write({'campaign_id': value, 'action_id': False})
        elif type == 'action':
            action = action_obj.browse(value)
            operation.write({'campaign_id': action.campaign_id.id, 'action_id': value})
        elif type == 'archive':
            operation.write({'archived': True})
        res = {operation.id: {'id': operation.id}}
        return json.dumps(list(res.values()))

    @http.route('/campaign/create/<string:name>', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def campaign_create(self, name):
        campaign_obj = http.request.env['sale.campaign']
        partner = http.request.env.user.partner_id.get_parent()
        campaign = campaign_obj.create({'name': name,
                                        'partner_id': partner.id})
        res = {campaign.id: {'name': campaign.name, 'id': campaign.id}}
        return json.dumps(list(res.values()))

    @http.route('/operation/message/list/<int:operation_id>', type='http', auth='user', methods=['POST'], website=True,
                csrf=False)
    def get_message_list(self, operation_id):
        operation_obj = http.request.env['sale.operation']
        operation = operation_obj.browse(operation_id)
        res = []
        for msg in operation.sudo().message_ids.filtered(lambda m: m.stage == 'stage_02'):
            res.append({'author': msg.author_id.name,
                        'body': msg.body or msg.message_body,
                        'date': operation_obj._get_date_tz(msg.date)})
        result = {operation.id: res}
        return json.dumps(list(result.values()))

    @http.route('/operation/message/list/child/<int:operation_id>', type='http', auth='user', methods=['POST'], website=True,
                csrf=False)
    def get_message_list_child(self, operation_id):
        operation_obj = http.request.env['sale.operation.child']
        operation_parent_obj = http.request.env['sale.operation']
        operation = operation_obj.browse(operation_id)
        res = []
        for msg in operation.sudo().message_ids.filtered(lambda m: m.stage == 'stage_02'):
            res.append({'author': msg.author_id.name,
                        'body': msg.body or msg.message_body,
                        'date': operation_parent_obj._get_date_tz(msg.date)})
        result = {operation.id: res}
        return json.dumps(list(result.values()))

    @http.route('/action/create/<string:name>/<int:campaign_id>', type='http', auth='user', methods=['POST'],
                website=True, csrf=False)
    def action_create(self, name, campaign_id):
        action_obj = http.request.env['sale.campaign.action']
        action = action_obj.create({'name': name,
                                    'campaign_id': campaign_id})
        res = {action.id: {'name': action.name, 'id': action.id}}
        return json.dumps(list(res.values()))

    @http.route('/contact/us', auth='public', methods=['POST'], website=True, csrf=False)
    def make_contact(self, **kwargs):
        crm_obj = http.request.env['crm.lead']
        contact_name = kwargs.get('name', '') + ' ' + kwargs.get('surname', '')
        company_name = kwargs.get('company')
        job = kwargs.get('function')
        email_from = kwargs.get('email_from')
        phone = kwargs.get('phone')
        crm_obj.sudo().create({
            'name': contact_name.upper(),
            'partner_name': company_name.upper(),
            'title': int(kwargs.get('title', 1)),
            'contact_name': contact_name.upper(),
            'function': job,
            'email_from': email_from,
            'phone': phone
        })
        return http.request.redirect('/')

    @http.route('/campaign/update/<string:name>/<int:campaign_id>', type='http', auth='user', methods=['POST'],
                website=True, csrf=False)
    def campaign_update(self, name, campaign_id):
        campaign_obj = http.request.env['sale.campaign']
        campaign = campaign_obj.browse(campaign_id)
        campaign.write({'name': name})
        res = {campaign.id: {'name': campaign.name, 'id': campaign_id}}
        return json.dumps(list(res.values()))

    @http.route('/campaign/delete/<int:campaign_id>', type='http', auth='user', methods=['POST'],
                website=True, csrf=False)
    def campaign_delete(self, campaign_id):
        campaign_obj = http.request.env['sale.campaign']
        campaign = campaign_obj.browse(campaign_id)
        res = {campaign.id: {'unlink': True}}
        campaign.sudo().unlink()
        return json.dumps(list(res.values()))

    @http.route('/action/delete/<int:action_id>', type='http', auth='user', methods=['POST'],
                website=True, csrf=False)
    def action_delete(self, action_id):
        action_obj = http.request.env['sale.campaign.action']
        action = action_obj.browse(action_id)
        res = {action.id: {'unlink': True}}
        action.sudo().unlink()
        return json.dumps(list(res.values()))

    @http.route(['/operation/download/<int:operation_id>'], type='http', auth="user", website=True)
    def download_operation(self, operation_id):
        operation_obj = http.request.env['sale.operation.child']
        operation = operation_obj.browse(operation_id)
        operation.command_download()
        if operation.modeled_file_url:
            return http.request.redirect(operation.modeled_file_url)
        else:
            return http.request.redirect('/operation/list')

    @http.route('/action/update/<string:name>/<int:action_id>', type='http', auth='user', methods=['POST'],
                website=True, csrf=False)
    def action_update(self, name, action_id):
        action_obj = http.request.env['sale.campaign.action']
        action = action_obj.browse(action_id)
        action.write({'name': name})
        res = {action.id: {'name': action.name, 'id': action_id}}
        return json.dumps(list(res.values()))

    @http.route('/operation/cancel', auth='user', methods=['POST'], website=True, csrf=False)
    def cancel_operation(self, **kwargs):
        operation_obj = http.request.env['sale.operation.child']
        operation_parent_obj = http.request.env['sale.operation']
        if kwargs.get("parent", False):
            if kwargs.get("parent") == 'parent':
                operation = operation_parent_obj.browse(int(kwargs.get('operation_id')))
                operation.button_cancel()
            elif kwargs.get("parent") == 'child':
                operation = operation_obj.browse(int(kwargs.get('operation_id')))
                operation.command_cancel()
        return http.request.redirect('/operation/list')

    @http.route('/operation/delete', auth='user', methods=['POST'], website=True, csrf=False)
    def delete_operation(self, **kwargs):
        operation_obj = http.request.env['sale.operation.child']
        operation_parent_obj = http.request.env['sale.operation']
        if kwargs.get("parent", False):
            if kwargs.get("parent") == 'parent':
                operation = operation_parent_obj.browse(int(kwargs.get('operation_id')))
                operation.button_delete()
            elif kwargs.get("parent") == 'child':
                operation = operation_obj.browse(int(kwargs.get('operation_id')))
                operation.command_delete()
        return http.request.redirect('/operation/list')

    @http.route('/operation/validate/<int:operation_id>', type='http', auth='user',
                methods=['POST'], website=True, csrf=False)
    def validate_operation(self, operation_id, **kwargs):
        operation_obj = http.request.env['sale.operation.child']
        operation = operation_obj.browse(operation_id)
        partner = http.request.env.user.partner_id.get_parent()
        subscription = partner.get_active_subscription()
        try:
            boolean = operation.command_ordered()
            if isinstance(boolean, bool):
                res = {operation.id: {'id': operation.id, 'show_popup': False, 'except': False}}
                return json.dumps(list(res.values()))
            res = {operation.id: {'id': operation.id, 'show_popup': True,
                                  'available_identifiers': subscription.balance,
                                  'volume_filled': operation.qty_extracted, 'difference': subscription.balance - operation.qty_extracted,
                                  'product_name': boolean['context'].get('product_name'),
                                  'except': False, 'text': False}}
        except Exception as e:
            res = {operation.id: {'id': operation.id, 'show_popup': True, 'except': True, 'text': e.args[0]}}

        return json.dumps(list(res.values()))

    @staticmethod
    def _get_path():
        module_path = modules.get_module_path('maas_website')
        if '\\' in module_path:
            src_path = '\\static\\src'
            src_report_path = '\\static\\src\\report\\'
        else:
            src_path = '/static/src'
            src_report_path = '/static/src/report/'
        return module_path, src_path, src_report_path

    @http.route('/report/<int:operation_id>', type='http', auth='user', methods=['POST'], website=True, csrf=False)
    def get_report_bi(self, operation_id):
        operation_obj = http.request.env['sale.operation']
        operation = operation_obj.browse(operation_id)
        report_bi_src = b"""
<!DOCTYPE html>
<head>
    <meta name="viewport" content="width=device-width">
    <meta charset="utf-8">
    <title>Power BI embedded - Conexance</title>
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="es6-promise.js"></script>
    <script src="powerbi.js"></script>
</head>
<body>

    <div id=embedContainer style="height:600px; width:100%; max-width:10000px;">
    </div>

    <!--Add script to update the page and send messages.-->
    <script type="text/javascript">
        $(function () {

            $.getJSON(""" + '"{}"'.format(operation.pbi_function_app_url).encode() + b""")
            .done(function( json ) {
                console.log(json.ErrorMessage);
                console.log(json.PowerBiEmbedInfo.EmbedToken);
                console.log(json.PowerBiEmbedInfo.ReportEmbedUrl);
                console.log(json.PowerBiEmbedInfo.ReportId);


            // Get models. models contains enums that can be used.
            var models = window['powerbi-client'].models;

            // We give All permissions to demonstrate switching between View and Edit mode and saving report.
            var permissions = models.Permissions.All;

            // Build the filter you want to use. For more information, See Constructing
            // Filters in https://github.com/Microsoft/PowerBI-JavaScript/wiki/Filters.
            const filter = {
            $schema: "http://powerbi.com/product/schema#basic",
            target: {
                table: """ + '"{}"'.format(operation.pbi_table_filter).encode() + b""", //Table contenant la colonne sur laquelle on souhaite filtrer
                column: """ + '"{}"'.format(operation.pbi_column_filter).encode() + b""" //Colonne filtre
            },
            operator: "In",
            values: [""" + '"{}"'.format(operation.pbi_value_filter).encode() + b"""], //Valeur du filtre
            filterType: models.FilterType.BasicFilter
            };


            // Embed configuration used to describe the what and how to embed.
            // This object is used when calling powerbi.embed.
            // This also includes settings and options such as filters.
            // You can find more information at https://github.com/Microsoft/PowerBI-JavaScript/wiki/Embed-Configuration-Details.
            var config= {
                type: 'report',
                tokenType: models.TokenType.Embed,
                accessToken: json.PowerBiEmbedInfo.EmbedToken,
                embedUrl: json.PowerBiEmbedInfo.ReportEmbedUrl,
                id: json.PowerBiEmbedInfo.ReportId,
                permissions: permissions,
                filters: [filter],
                settings: {
                    filterPaneEnabled: false,
                    navContentPaneEnabled: true
                }
            };

            // Get a reference to the embedded report HTML element
            var embedContainer = $('#embedContainer')[0];

            // Embed the report and display it within the div container.
            var report = powerbi.embed(embedContainer, config);
            })
            .fail(function( jqxhr, textStatus, error ) {
                var err = textStatus + ", " + error + "(status=" + jqxhr.status + ")";
                console.log( "REQUEST HAS FAILED - SIMPLE ERROR MESSAGE: " + err);

                if(jqxhr.responseJSON.ErrorMessage)
                {
                    console.log( "REQUEST HAS FAILED - DETAILED ERROR MESSAGE: " + jqxhr.responseJSON.ErrorMessage );
                }
            });
        });
     </script>
</body>
</html>
"""
        if operation.pbi_function_app_url:
            module_path, src_path, src_report_path = self._get_path()
            os.chdir("{0}{1}".format(module_path, src_path))
            if not os.path.exists('report'):
                os.makedirs('report')

            file_path = "{0}{1}".format(module_path + src_report_path + str(operation.access_token),
                                        '.html')
            if not os.path.exists(str(operation.access_token)):
                current_file = open(file_path, 'w+b')
            else:
                current_file = open(file_path, 'r+b')
            current_file.write(report_bi_src)
            current_file.close()

        result = {
            operation.id: {'id': operation_id,
                           'report_bi_src': "{0}{1}{2}".format('/maas_website/static/src/report/',
                                                               operation.access_token,
                                                               '.html')}}
        return json.dumps(list(result.values()))

    @http.route('/close/report/<int:operation_id>', auth='user', methods=['POST'], website=True, csrf=False)
    def close_report(self, operation_id):
        operation_obj = http.request.env['sale.operation']
        operation = operation_obj.browse(int(operation_id))
        if operation.pbi_function_app_url:
            module_path, src_path, src_report_path = self._get_path()
            os.chdir("{0}{1}".format(module_path, src_path))
            file_path = "{0}{1}".format(module_path + src_report_path + str(operation.access_token), '.html')
            if os.path.exists(file_path):
                os.remove(file_path)
        result = {operation.id: {'id': operation.id}}
        return json.dumps(list(result.values()))

    @http.route('/operation/contact', auth='user', website=True)
    def render_contact(self):
        quantity, identifiers, percent, unlimited = self._get_consumption_data()
        partner = http.request.env.user.partner_id.get_parent()
        values = {
            'campaign_ids': partner.campaign_ids,
            'total_qty_cumulative': quantity,
            'identifiers': identifiers,
            'percent': percent,
            'url_for': url_for,
            'unlimited': unlimited
        }
        return http.request.render('maas_website.operation_contact', values)

    @http.route('/operation/session/check', methods=['POST'], website=True, csrf=False)
    def session_check(self):
        print(http.request.session.uid)
        values = {'connected': http.request.session.uid}
        return json.dumps(values)

    @http.route('/operation/filter/get', auth='user', methods=['POST'], website=True, csrf=False)
    def get_filter(self):
        user_obj = http.request.env['res.users'].sudo()
        user = user_obj.browse(http.request.env.user.id)
        filter = user.portal_filter
        values = {'filter': filter}
        return json.dumps(values)

    @http.route('/operation/filter/set/<string:filter>', auth='user', methods=['PUT'], website=True, csrf=False)
    def set_filter(self, filter):
        user_obj = http.request.env['res.users'].sudo()
        user = user_obj.browse(http.request.env.user.id)
        user.sudo().write({'portal_filter': filter})
        values = {user.id: {'filter': filter}}
        return json.dumps(list(values))

    @http.route('/operation/indication', auth='user', website=True, csrf=False)
    def indication(self):
        quantity, identifiers, percent, unlimited = self._get_consumption_data()
        partner = http.request.env.user.partner_id.get_parent()
        indications = http.request.env['partner.indication.infos'].sudo().search(
            [('partner_id', '=', partner.id), ('active', '=', True)], order="sequence asc")
        values = {
            'campaign_ids': partner.campaign_ids,
            'total_qty_cumulative': quantity,
            'identifiers': identifiers,
            'percent': percent,
            'url_for': url_for,
            'unlimited': unlimited,
            'indications': indications,
            'partner': partner,
        }
        return http.request.render('maas_website.indication', values)
