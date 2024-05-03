# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
import contextlib
import io
from odoo.exceptions import ValidationError
from odoo.addons.choreograph_sage.models.res_partner import PAYMENT_CHOICE


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_choice = fields.Selection(PAYMENT_CHOICE, string='Payment Choice')
    wording = fields.Char(compute='_compute_wording')
    is_transferred_to_sage = fields.Boolean()

    @api.depends('name', 'partner_id', 'partner_id.name')
    def _compute_wording(self):
        for rec in self:
            rec.wording = "%s / %s" % (rec.partner_id.name, rec.name)

    @api.model_create_multi
    def create(self, values):
        res = super(AccountMove, self).create(values)
        for move in res:
            if move.partner_id:
                move.update_payment_choice_from_partner()
        return res

    def update_payment_choice_from_partner(self):
        self.payment_choice = self.partner_id.payment_choice

    def generate_sage_file(self, move_type, limit=None):
        ftp_server = self.env['choreograph.sage.ftp.server'].search([], limit=1)
        if not ftp_server:
            raise ValidationError(_('Make sure to configure an active FTP server!'))

        if move_type == 'in':
            move_types = ['in_invoice', 'in_refund']
        elif move_type == 'out':
            move_types = ['out_invoice', 'out_refund']

        moves = self.env['account.move'].search([('move_type', 'in', move_types), ('state', '=', 'posted'),
                                                 ('is_transferred_to_sage', '=', False)], limit=limit)
        if moves:
            file = self.create_sage_file(moves)
            # TODO: send the file to the the server and create LOG
            moves.write({
                'is_transferred_to_sage': True,
            })

    def create_sage_file(self, moves):
        """
        Create the binary file
        :param moves: account_move
        :return: return the binary file
        """
        with contextlib.closing(io.BytesIO()) as buf:
            wrapper = io.TextIOWrapper(
                buf,
                encoding='utf-8',
                write_through=True,
            )
            # TODO: get the fields values from moves
            wrapper.write('TEST SAGE FILE' + '\n')
            out = base64.encodebytes(buf.getvalue())
        return out
