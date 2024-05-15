# -*- coding: utf-8 -*-

from odoo import models, fields, api
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
        if move_type == 'in':
            move_types = ['in_invoice', 'in_refund']
        elif move_type == 'out':
            move_types = ['out_invoice', 'out_refund']

        move_ids = self.env['account.move'].search([('move_type', 'in', move_types), ('is_transferred_to_sage', '=', False)], limit=limit)
        if move_ids:
            # TODO: generate the file and send to the FTP server
            move_ids.write({
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
        
        type = moves[-1].move_type
                
        for line in moves.line_ids:
            if type in ['in_invoice', 'in_refund']:
                role = line.move_id.partner_id.third_party_role_supplier_code
            else:
                role = line.move_id.partner_id.third_party_role_client_code
            
            vals= {
                "Code Société":"",
                "Journal": 'ACH' if type == 'in' else 'VTE',
                "Type de Pièce":'FF' if type == 'in' else 'FC',
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
        
        file_name = f"{datetime.now().strftime('%Y-%m-%d %H:%M')}.csv"
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
            self.create_ftp_log(state, type, message,file=None, file_name=None, line_count=None)      
        finally:
            ssh_client.close()
        return True
