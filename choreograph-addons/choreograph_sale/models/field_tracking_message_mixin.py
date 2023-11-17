# -*- coding: utf-8 -*-

import logging

from odoo import api, fields, models, _
from odoo.tools import html_escape
from odoo.tools.misc import format_date

from odoo.exceptions import MissingError

_logger = logging.getLogger(__name__)

class FieldTrackingMessageMixin(models.AbstractModel):
    _name = 'field.tracking.message.mixin'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Field Tracking Message Mixin'

    def _field_to_track(self):
        return []

    def _format_tracked_field(self):
        self.ensure_one()
        res = "<ul>"
        for field_name in self._field_to_track():
            field_obj = self._fields[field_name]
            if getattr(self, field_name):
                if field_obj.type == "date":
                    field_value = format_date(self.env, getattr(self, field_name), date_format="dd/MM/yyyy")
                elif field_obj.type == "many2one":
                    field_value = getattr(self, field_name).display_name
                elif field_obj.type == "selection":
                    field_desc = field_obj.get_description(self.env)
                    field_info = dict(field_desc.get('selection'))
                    field_value = field_info.get(getattr(self, field_name))
                elif field_obj.type in ["one2many", "many2many"]:
                    field_value = ", ".join(getattr(self, field_name).mapped("display_name"))
                else:
                    field_value = getattr(self, field_name)
            else:
                field_value = _("<span class='text-muted'><i>Empty</i></span>")
            res += f"<li>{field_value} <i>({html_escape(field_obj._description_string(self.env))})</i></li>"
        res += "</ul>"
        return res

    def _log_field_message(self, body_msg):
        for rec in self:
            if rec._field_to_track():
                body_msg += rec._format_tracked_field()
            project_id = self._get_project_id()
            if project_id and project_id.stage_id.stage_number != '10':
                project_id.message_post(body=body_msg,
                                        partner_ids=project_id.message_follower_ids.mapped('partner_id').ids)

    def _get_project_id(self):
        return self.order_id.project_ids[0] if self.order_id.project_ids else False

    @api.model
    def _track_message_title_unlink(self):
        return

    @api.model
    def _track_message_title_create(self):
        doc_name = self.env['ir.model']._get(self._name).name
        return _('%s created', doc_name)

    def unlink(self):
        if self._track_message_title_unlink():
            for rec in self:
                rec._log_field_message(rec._track_message_title_unlink())
        return super(FieldTrackingMessageMixin, self).unlink()

    @api.model_create_multi
    def create(self, vals):
        res = super(FieldTrackingMessageMixin, self).create(vals)
        if self._track_message_title_create():
            res._log_field_message(res._track_message_title_create())
        return res

    def _creation_message(self):
        return ""

    def _message_track(self, fields_iter, initial_values_dict):
        if not fields_iter:
            return {}

        tracked_fields = self.fields_get(fields_iter)
        tracking = dict()
        for record in self:
            try:
                tracking[record.id] = record._mail_track(tracked_fields, initial_values_dict[record.id])
            except MissingError:
                continue

        # find content to log as body
        bodies = self.env.cr.precommit.data.pop(f'mail.tracking.message.{self._name}', {})
        for record in self:
            changes, tracking_value_ids = tracking.get(record.id, (None, None))
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtype = record._track_subtype(
                dict((col_name, initial_values_dict[record.id][col_name])
                     for col_name in changes)
            )
            if subtype:
                if not subtype.exists():
                    _logger.debug('subtype "%s" not found' % subtype.name)
                    continue
                record.message_post(
                    body=bodies.get(record.id) or '',
                    subtype_id=subtype.id,
                    tracking_value_ids=tracking_value_ids
                )
            elif tracking_value_ids:
                project_id = record._get_project_id()
                if project_id:
                    project_id.message_post(
                        body=record._get_body_message_track(),
                        tracking_value_ids=tracking_value_ids,
                        partner_ids=project_id.message_follower_ids.mapped('partner_id').ids
                    )

        return tracking

    def _get_body_message_track(self):
        self.ensure_one()
        return f"{self.sequence}"
