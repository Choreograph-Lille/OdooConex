# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools import html_escape
from odoo.tools.misc import format_date


class FieldTrackingMessageMixin(models.AbstractModel):
    _name = 'field.tracking.message.mixin'
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
            rec._message_log(body=body_msg)

    @api.model
    def _track_message_title_unlink(self):
        return

    def unlink(self):
        if self._track_message_title_unlink():
            for rec in self:
                rec._log_field_message(rec._track_message_title_unlink())
        return super(FieldTrackingMessageMixin, self).unlink()

    def _creation_message(self):
        res = super()._creation_message()
        if self._field_to_track():
            res += self._format_tracked_field()
        return res
