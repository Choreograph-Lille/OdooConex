# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import base64
import csv
from datetime import datetime
import paramiko
from odoo.exceptions import ValidationError
from odoo.addons.choreograph_sage.models.res_partner import PAYMENT_CHOICE


class AccountMove(models.Model):
    _inherit = "account.move"

    payment_choice = fields.Selection(PAYMENT_CHOICE, compute='compute_payment_choice', inverse='inverse_payment_choice', string='Payment Choice', store=True)
    wording = fields.Char(compute='_compute_wording')
    is_transferred_to_sage = fields.Boolean()

    @api.depends('partner_id','move_type')
    def compute_payment_choice(self):
        for rec in self:
            if rec.move_type in ['in_invoice', 'in_refund']:
                rec.payment_choice = rec.partner_id.supplier_payment_choice
               
            elif rec.move_type in ['out_invoice', 'out_refund']:
                rec.payment_choice = rec.partner_id.customer_payment_choice
            else:
                rec.payment_choice = False
                

    def inverse_payment_choice(sefl):
        pass

    @api.depends('name', 'partner_id', 'partner_id.name')
    def _compute_wording(self):
        for rec in self:
            rec.wording = "%s-%s" % (rec.partner_id.name, rec.name)


    def generate_sage_file(self, move_type, limit=None):
        ftp_server = self.env['choreograph.sage.ftp.server'].search([('active','=',True)], limit=1)
        if not ftp_server:
            raise ValidationError(_('Make sure to configure an active FTP server!'))

        if move_type == 'in':
            move_types = ['in_invoice', 'in_refund']
        elif move_type == 'out':
            move_types = ['out_invoice', 'out_refund']

        moves = self.env['account.move'].search([('move_type', 'in', move_types), ('state', '=', 'posted'),
                                                 ('is_transferred_to_sage', '=', False)], limit=limit)
        if moves:
            self.create_sage_file(moves, ftp_server)
            
            # TODO: send the file to the the server and create LOG
            moves.write({
                'is_transferred_to_sage': True,
            })

    def prepare_file_rows(self, moves):
        """
        Prepare rows value ofr the binary file
        :param moves: account_move
        :return: Array
        """
        fields = [
            "Code Société",
            "Journal",
            "Type de Pièce",
            "Compte général",
            "Rôle Tiers",
            "date piece",
            "date échéance",
            "Mode reglement",
            "Référence Pièce",
            "Libellé",
            "Devise",
            "Débit devise",
            "Crédit Devise",
            "Débit EUR",
            "Crédit EUR",
            "Libellé CARTESIS",
            "codeCARTESIS",
            "Département",
            "Média",
            "ProfilTVA",
            "NUMDEVIS",
            "JOUMM",
            "IDODOO"
        ]
        rows = []                
                
        for line in moves.line_ids:
            if line.move_id.move_type in ['in_invoice', 'in_refund']:
                role = line.move_id.partner_id.third_party_role_supplier_code
                ref = 'FF' if line.move_id.move_type == 'in_invoice' else 'AF'
            else:
                role = line.move_id.partner_id.third_party_role_client_code
                ref = 'FC' if line.move_id.move_type == 'out_invoice' else 'AC'
            
            vals= {
                "Code Société":"",
                "Journal": line.move_id.journal_id.code,
                "Type de Pièce":ref,
                "Compte général":line.account_id.code or "",
                "Rôle Tiers":role or "",
                "date piece":line.move_id.invoice_date or "",
                "date échéance":line.move_id.invoice_date_due or "",
                "Mode reglement":line.move_id.payment_choice or "",
                "Référence Pièce":line.move_id.name or "",
                "Libellé":line.move_id.wording or "",
                "Devise":line.move_id.currency_id.name or "",
                "Débit devise":line.debit,
                "Crédit Devise":line.credit,
                "Débit EUR":"",
                "Crédit EUR":"",
                "Libellé CARTESIS":"",
                "codeCARTESIS":line.move_id.partner_id.cartesis_code or "",
                "Département":"",
                "Média":"",
                "ProfilTVA":','.join(line.tax_ids.filtered(lambda l:l.tva_profile_code !=False).mapped("tva_profile_code")),
                "NUMDEVIS":line.move_id.invoice_origin or "",
                "JOUMM":"",
                "IDODOO":line.id
            }
            rows.append(vals)
        return fields, rows

    def create_ftp_log(self, state, type, file=None, file_name=None, line_count=None, message=None):
        """
        Create FTP log
        :param : state, file, file_name, line_count, message
        :return: ftp.logging
        """
        log_vals = {
            "export_date": datetime.today(),
            "file_name":file_name,
            "line_count": line_count,
            "message": message,
            "state":state,
            "type":type
        }
        if file:
            attachment_vals = {
                'datas': file,
                'name': file_name,
            }            
            attachment_id = self.env['ir.attachment'].create(attachment_vals)
            log_vals['attachment_id'] = attachment_id.id
        log = self.env['ftp.logging'].create(log_vals)
        return log

    def create_sage_file(self, moves, ftp_server):
        """
        Create the binary file
        :param moves: account_move
        :return: Boolean
        """       
        # Establish SSH connection
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #Get path of key as attachment
        key_path = ftp_server.key_attachment_id._full_path(ftp_server.key_attachment_id.store_fname)
        passphrase = ftp_server.passphrase
        fields, rows = self.prepare_file_rows(moves)
        type = 'supplier' if moves[-1].move_type in ['in_invoice', 'in_refund'] else 'customer'
        
        file_name = f"{'ECRACH' if type == 'supplier' else 'ECRVEN'}_{datetime.today().strftime('%Y%m%d')}.csv"
        try:
            key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
            ssh_client.connect(ftp_server.host, ftp_server.port, ftp_server.username, pkey=key)
            # Create and Transfert file
            with paramiko.SFTPClient.from_transport(ssh_client.get_transport()) as sftp:
                # Create temporary file
                with open(file_name, 'w', newline='') as temp_file:
                    writer = csv.DictWriter(temp_file, delimiter='\t',fieldnames = fields)                    
                    writer.writeheader()
                    writer.writerows(rows)
                # Copy temporary file into server
                sftp.put(file_name, f"{ftp_server.path}/{file_name}")
                # Create log
                with open(file_name,'rb') as file:
                    file = base64.b64encode(file.read())
                    state = 'success'
                    message = _("File uploaded with success")
                    self.create_ftp_log(state, type, file, file_name, len(moves), message)
        except Exception as e:
            state = 'failed'
            message = str(e)
            self.create_ftp_log(state, type, message)      
        finally:
            ssh_client.close()
        return True
