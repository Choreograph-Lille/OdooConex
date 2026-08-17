from odoo import fields, models, api

UBL_NOTES_DEFAULT = """#AAB#Aucun escompte accordé pour paiement anticipé.
#PMD#Les pénalités appliquées en cas de retard de paiement seront 1,5 fois le taux de l'interêt légal (loi n°92-1442 du 31.12.1992).
#PMT#En cas de retard de paiement, le débiteur sera redevable de plein de droit d'une indemnité forfaitaire pour frais de recouvrement de 40 euros, et ce, sans préjudice de tout autre droit ou recours dont dispose le créancier.
#AAI#Banque : HSBC Centre d'affaire entreprises Trocadero-112 Avenue Kleber-75116 PARIS.
#AAI#RIB : 30056 00936 09360002867 34
#AAI#IBAN : FR76 3005 6009 3609 3600 0286 734
#AAI#BIC : CCFRFRPP"""

class ResCompany(models.Model):
    _inherit = 'res.company'

    new_address = fields.Html()
    siren = fields.Char(string="SIREN")
    electronic_address = fields.Char(string="Electronic Address")
    ubl_notes = fields.Text(
        string='UBL Notes'
    )
    
    def get_electronic_address(self):
        """Return the electronic address of the company or its partner if not set."""
        self.ensure_one()
        return self.electronic_address or self.partner_id.electronic_address
    
    @api.model
    def _init_ubl_notes_default(self):
        """Init UBL note on the main company if not set."""
        main_company = self.env.ref('base.main_company', raise_if_not_found=False)
        if main_company and not main_company.ubl_notes:
            main_company.ubl_notes = UBL_NOTES_DEFAULT
