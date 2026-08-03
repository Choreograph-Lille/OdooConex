# -*- coding: utf-8 -*-

import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

from odoo import api, fields, models, _

AUTHORIZED_PAYMENT_STATE = ('En paiement', 'Extourné')

class AccountMove(models.Model):
    _inherit = 'account.move'

    def get_file_name(self):
        file_name = super(AccountMove, self).get_file_name()
        move_type = self.env.context.get('move_type')
        if move_type == 'in_invoice':
            config_parameter = self.env['ir.config_parameter'].sudo()
            prefix = config_parameter.get_param('choreograph_sage_purchase_account.prefix') or False
            suffix = config_parameter.get_param('choreograph_sage_purchase_account.suffix') or False
            sage_date_str = config_parameter.get_param('choreograph_sage_purchase_account.sage_file_date') or False
            sage_date = fields.Date.from_string(sage_date_str) if sage_date_str else fields.Date.today()

            file_name = f"{sage_date.strftime('%Y%m%d')}.csv"
            if prefix:
                file_name = f"{prefix}_{file_name}"
            if suffix:
                file_name = f"{file_name}_{suffix}"
        return file_name

    @api.model
    def import_account_move_in_invoice(self):
        move_type = 'in_invoice'
        self = self.with_context(move_type=move_type)
        sftp_server_param = self.env['ir.config_parameter'].sudo().get_param('choreograph_sage_sftp_import.sftp_server_id', False)
        sftp_server_id = self.env['choreograph.sage.sftp.server'].browse(int(sftp_server_param)) if sftp_server_param else False
        if sftp_server_id:
            ssh_client = self.get_sftp_client_import(sftp_server_id)
            start = datetime.now()
            log = self.create_sftp_log(sftp_server_id,'purchase')
            datas = self.download_file(sftp_server_id, ssh_client, log)
            if len(datas) == 0:
                log.state = 'rejected'
                return False

            line_count = 0
            error_count = 0
            success_count = 0
            for data in datas:
                try:
                    move_id = self.validate_data_import(data, log, move_type)
                    if move_id:
                        payment_state = data.get('Statut paiement')
                        if move_id.amount_residual > 0 and payment_state == 'En paiement':
                            move_id.create_payment(payment_date=data.get('Date paiement'))
                            success_count +=1
                        else:
                            self.create_sftp_log_line(
                                log=log,
                                message=_("Invoice cannot be paid; please check the remaining balance or whether a reversal has already been created."),                                error_type="data_mismatch",
                                ref=data.get("Référence Pièce"),
                            )
                            error_count += 1

                    else:
                        error_count += 1
                except Exception as e:
                    _logger.exception(
                        "Unexpected error while processing line with reference '%s'",
                        data.get("Référence Pièce")
                    )
                    self.create_sftp_log_line(
                        log=log,
                        message=str(e),
                        error_type="file_invalid",
                        ref=data.get("Référence Pièce"),
                    )
                    error_count += 1
                finally:
                    line_count += 1
            log.line_count = line_count
            log.error_count = error_count
            log.success_count = success_count
            if line_count == error_count:
                log.state = 'failed'
            elif line_count == success_count:
                log.state = 'success'
            elif error_count != line_count and error_count != 0 and line_count != 0:
                log.state = 'partial'
            end = datetime.now()
            log.duration = (end - start).seconds
