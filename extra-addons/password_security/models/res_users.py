# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re
import logging
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


def delta_now(**kwargs):
    dt = datetime.now() + timedelta(**kwargs)
    return fields.Datetime.to_string(dt)


class ResUsers(models.Model):
    _inherit = 'res.users'

    password_write_date = fields.Datetime(
        'Last password update',
        readonly=True,
    )
    password_history_ids = fields.One2many(
        string='Password History',
        comodel_name='res.users.pass.history',
        inverse_name='user_id',
        readonly=True,
    )

    @api.model
    def create(self, vals):
        vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).create(vals)

    def write(self, vals):
        if vals.get('password'):
            self.check_password(vals['password'])
            vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).write(vals)

    def password_match_message(self):
        self.ensure_one()
        company_id = self.company_id
        message = []
        if company_id.password_lower:
            message.append(', ' + _('Lowercase letter'))
        if company_id.password_upper:
            message.append(', ' + _('Uppercase letter'))
        if company_id.password_numeric:
            message.append(', ' + _('Numeric digit'))
        if company_id.password_special:
            message.append(', ' + _('Special character'))
        if len(message):
            message[-1] = message[-1]+'.'
        if len(message):
            message = [_(' Must contain the following: ')] + message
        if company_id.password_length:
            message = [
                _('Password must be %d characters or more.') %
                company_id.password_length
            ] + message
        return_message = list(''.join(message))
        return_message[''.join(message).find(',')] = ''
        return_message[''.join(message).rfind(',')] = ' '+_(' and ')
        return_message = ''.join(return_message)
        return ''.join(return_message)

    def check_password(self, password):
        self.ensure_one()
        if not password:
            return True
        company_id = self.company_id
        password_regex = ['^']
        if company_id.password_lower:
            password_regex.append('(?=.*?[a-z])')
        if company_id.password_upper:
            password_regex.append('(?=.*?[A-Z])')
        if company_id.password_numeric:
            password_regex.append(r'(?=.*?\d)')
        if company_id.password_special:
            password_regex.append(r'(?=.*?\W)')
        password_regex.append('.{%d,}$' % company_id.password_length)
        if not re.search(''.join(password_regex), password):
            raise ValidationError(_(self.password_match_message()))
        return True

    def _password_has_expired(self):
        self.ensure_one()
        if not self.password_write_date:
            return True
        write_date = fields.Datetime.from_string(self.password_write_date)
        today = fields.Datetime.from_string(fields.Datetime.now())
        days = (today - write_date).days
        return days > self.company_id.password_expiration

    def action_expire_password(self):
        expiration = delta_now(days=+1)
        for rec_id in self:
            rec_id.mapped('partner_id').signup_prepare(
                signup_type="reset", expiration=expiration
            )

    def _validate_pass_reset(self):
        """ It provides validations before initiating a pass reset email
        :raises: PassError on invalidated pass reset attempt
        :return: True on allowed reset
        """
        for rec_id in self:
            pass_min = rec_id.company_id.password_minimum
            if pass_min <= 0:
                pass
            write_date = fields.Datetime.from_string(
                rec_id.password_write_date
            )
            delta = timedelta(hours=pass_min)
            if write_date + delta > datetime.now():
                raise ValidationError(
                    _('Passwords can only be reset every %d hour(s). '
                      'Please contact an administrator for assistance.') %
                    pass_min,
                )
        return True


    def _set_password(self):
        """ It validates proposed password against existing history
        :raises: PassError on reused password
        """
        crypt = self._crypt_context()
        for rec_id in self:
            recent_passes = rec_id.company_id.password_history
            if recent_passes < 0:
                recent_passes = rec_id.password_history_ids
            else:
                recent_passes = rec_id.password_history_ids[
                    0:recent_passes-1
                ]
            if len(recent_passes.filtered(
                lambda r: crypt.verify(rec_id.password, r.password_crypt)
            )):
                message = self.password_match_message()[:-1]
                raise ValidationError(
                    message + _(' and cannot use the most recent %d passwords.') %
                    rec_id.company_id.password_history
                )
        super(ResUsers, self)._set_password()

    def _set_encrypted_password(self, uid, encrypted):
        """ It saves password crypt history for history rules """
        super(ResUsers, self)._set_encrypted_password(uid, encrypted)
        self.write({
            'password_history_ids': [(0, 0, {
                'password_crypt': encrypted,
            })],
        })

    def init(self):
        _logger.info("Hashing password was commented due to server error in password_security module")
        #self.env.cr.execute("SELECT id, password FROM res_users"
                   #" WHERE password IS NOT NULL"
                   #"   AND password != ''")
        #for uid, pwd in self.env.cr.fetchall():
            #self.sudo().browse(uid)._set_password(pwd)
