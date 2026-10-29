# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, Command
from lxml import etree
TYPE_REVERSE_MAP = {
    'entry': 'entry',
    'out_invoice': 'out_refund',
    'out_refund': 'entry',
    'in_invoice': 'in_refund',
    'in_refund': 'entry',
    'out_receipt': 'out_refund',
    'in_receipt': 'in_refund',
}

class AccountMove(models.Model):
    _inherit = "account.move"

    sale_order_id = fields.Many2one("sale.order", "Sale Order", compute="_compute_sale_order_id", store=True, compute_sudo=True)
    user_id = fields.Many2one('res.users', tracking=False)
    is_confidential = fields.Boolean()
    provider_invoice_date = fields.Date()
    siren = fields.Char(compute='compute_siren', string='SIREN')
    is_ubl_norm_fr = fields.Boolean(compute='_compute_is_ubl_norm_fr', string='UBL EUR (French standard)')

    def action_invoice_sent(self):
        result = super(AccountMove, self).action_invoice_sent()
        template = self.env.ref("choreograph_account.email_template_edi_invoice", raise_if_not_found=False)
        result["context"].update({
            "default_use_template": bool(template),
            "default_template_id": template and template.id or False,
        })

        return result
    @api.depends('move_type', 'provider_invoice_date')
    def _compute_needed_terms(self):
        for invoice in self:
            if invoice.move_type == 'in_invoice' and invoice.provider_invoice_date:
                invoice = invoice.with_context(
                    provider_invoice_date=invoice.provider_invoice_date
                )
            super(AccountMove, invoice)._compute_needed_terms()
    
    @api.depends('move_type', 'provider_invoice_date')
    def _compute_invoice_date_due(self):
        for move in self:
            if move.move_type == 'in_invoice' and move.provider_invoice_date:
                # If provider_invoice_date is set, use it to compute invoice_date_due
                terms = move.needed_terms
                if terms:
                    move.invoice_date_due = terms and max(
                    (k['date_maturity'] for k in terms.keys() if k),
                    default=False,)
                else:
                    move.invoice_date_due = move.provider_invoice_date
            else:
                super(AccountMove, move)._compute_invoice_date_due()

    @api.depends('line_ids.sale_line_ids')
    def _compute_sale_order_id(self):
        for move in self:
            orders = move.line_ids.mapped("sale_line_ids").mapped("order_id")
            move.sale_order_id = orders and orders[0].id or False

    @api.model
    def _get_mail_partner(self):
        adresses = self.partner_id
        if self.partner_id.child_ids:
            adresses |= self.partner_id.child_ids.filtered(lambda rp: rp.type == 'invoice')
        return ','.join([str(rp.id) for rp in adresses])

    def _reverse_moves(self, default_values_list=None, cancel=False):
        ''' Override _reverse_moves function
        :return: An account.move recordset, reverse of the current self without posted.
        '''
        if not default_values_list:
            default_values_list = [{} for move in self]

        if cancel:
            lines = self.mapped('line_ids')
            # Avoid maximum recursion depth.
            if lines:
                lines.remove_move_reconcile()

        reverse_moves = self.env['account.move']
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'move_type': TYPE_REVERSE_MAP[move.move_type],
                'reversed_entry_id': move.id,
                'partner_id': move.partner_id.id,
            })
            reverse_moves += move.with_context(
                move_reverse_cancel=cancel,
                include_business_fields=True,
                skip_invoice_sync=move.move_type == 'entry',
            ).copy(default_values)

        reverse_moves.with_context(skip_invoice_sync=cancel).write({'line_ids': [
            Command.update(line.id, {
                'balance': -line.balance,
                'amount_currency': -line.amount_currency,
            })
            for line in reverse_moves.line_ids
            if line.move_id.move_type == 'entry' or line.display_type == 'cogs'
        ]})
        
        return reverse_moves
    
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.is_confidential = self.partner_id.is_confidential    
        if self.partner_id.property_product_pricelist:
            self.currency_id = self.partner_id.property_product_pricelist.currency_id

    @api.depends('partner_id')
    def compute_siren(self):
        for move_id in self:
            if move_id.partner_id.company_type != 'company':
                move_id.siren = move_id.partner_id.parent_id.siren
            else:
                move_id.siren = move_id.partner_id.siren
    
    def _ubl_add_header(self, parent_node, ns, version="2.1"):
        super()._ubl_add_header(parent_node, ns, version=version)

        cbc = ns["cbc"]

        if parent_node.find(cbc + 'CustomizationID') is None:
            customization_node = etree.Element(cbc + 'CustomizationID')
            customization_node.text = (
                'urn:cen.eu:en16931:2017#conformant#'
                'urn.cpro.gouv.fr:1p0:extended-ctc-fr'
            )
            parent_node.append(customization_node)

        if parent_node.find(cbc + 'ProfileID') is None:
            profile_node = etree.Element(cbc + 'ProfileID')
            profile_node.text = 'S1'
            parent_node.append(profile_node)

        # GBP invoices only: TaxCurrencyCode = EUR, placed right after
        # DocumentCurrencyCode (new UBL 2.1 regulation)
        if (
            self.currency_id == self.env.ref('base.GBP')
            and parent_node.find(cbc + 'TaxCurrencyCode') is None
        ):
            tax_currency_node = etree.Element(cbc + 'TaxCurrencyCode')
            tax_currency_node.text = 'EUR'
            doc_currency_node = parent_node.find(cbc + 'DocumentCurrencyCode')
            if doc_currency_node is not None:
                doc_currency_node.addnext(tax_currency_node)
            else:
                parent_node.append(tax_currency_node)

        code_pf = self.partner_id.commercial_partner_id.pf_code_identification
        if code_pf:
            note_node = etree.Element(cbc + "Note")
            note_node.text = "#BAR#%s" % code_pf
            parent_node.append(note_node)
            
        notes_pa = self.partner_id.notes_pa or self.commercial_partner_id.notes_pa
        if notes_pa:
            for note_node in parent_node.findall(cbc + 'Note'):
                parent_node.remove(note_node)

            if code_pf:
                note_bar = etree.Element(cbc + 'Note')
                note_bar.text = "#BAR#%s" % code_pf
                parent_node.append(note_bar)

            for ligne in notes_pa.splitlines():
                ligne = ligne.strip()
                if not ligne:
                    continue
                note = etree.Element(cbc + 'Note')
                note.text = ligne
                parent_node.append(note)

        correct_order = [
            cbc + 'UBLVersionID',
            cbc + 'CustomizationID',
            cbc + 'ProfileID',
            cbc + 'ProfileExecutionID',
            cbc + 'ID',
            cbc + 'CopyIndicator',
            cbc + 'UUID',
            cbc + 'IssueDate',
            cbc + 'IssueTime',
            cbc + 'DueDate',
            cbc + 'InvoiceTypeCode',
            cbc + 'CreditNoteTypeCode',
            cbc + 'Note',
            cbc + 'TaxPointDate',
            cbc + 'DocumentCurrencyCode',
            cbc + 'TaxCurrencyCode',
            cbc + 'PricingCurrencyCode',
            cbc + 'PaymentCurrencyCode',
            cbc + 'PaymentAlternativeCurrencyCode',
            cbc + 'AccountingCostCode',
            cbc + 'AccountingCost',
            cbc + 'LineCountNumeric',
        ]

        children = list(parent_node)
        children.sort(
            key=lambda c: correct_order.index(c.tag)
            if c.tag in correct_order else len(correct_order)
        )
        for child in children:
            parent_node.remove(child)
        for child in children:
            parent_node.append(child)

    def _ubl_add_tax_total(self, xml_root, ns, version="2.1"):
        if self._ubl_is_norm_fr():
            self._ubl_fr_add_tax_total(xml_root, ns, version=version)
        else:
            super()._ubl_add_tax_total(xml_root, ns, version=version)
        # GBP invoices only: TaxAmount (global and per VAT category) is expressed
        # in EUR. Only the currencyID attribute is changed, TaxableAmount stays
        # in the invoice currency.
        if self.currency_id != self.env.ref('base.GBP'):
            return
        tax_currency = 'EUR'
        for tax_total in xml_root.findall(ns["cac"] + "TaxTotal"):
            # Global TaxAmount (child of TaxTotal)
            tax_amount = tax_total.find(ns["cbc"] + "TaxAmount")
            if tax_amount is not None:
                tax_amount.set("currencyID", tax_currency)
            # TaxAmount per VAT category (child of TaxSubtotal)
            for subtotal in tax_total.findall(ns["cac"] + "TaxSubtotal"):
                sub_tax_amount = subtotal.find(ns["cbc"] + "TaxAmount")
                if sub_tax_amount is not None:
                    sub_tax_amount.set("currencyID", tax_currency)

    def _ubl_add_customer_party(
        self, partner, company, node_name, parent_node, ns, version="2.1"
    ):
        customer_party_root = super()._ubl_add_customer_party(
            partner, company, node_name, parent_node, ns, version=version
        )

        cac = ns["cac"]
        cbc = ns["cbc"]

        party_node = customer_party_root.find(cac + "Party")
        if party_node is None:
            return customer_party_root

        website_node = party_node.find(cbc + "WebsiteURI")
        if website_node is not None:
            party_node.remove(website_node)

        code_pf = (partner.commercial_partner_id.pf_code_identification or '').strip().upper()
        if self._ubl_is_norm_fr() and code_pf in ('B2BINT', 'B2C'):
            email = partner.email
            if email:
                endpoint_node = etree.Element(cbc + "EndpointID")
                endpoint_node.set("schemeID", "EM")
                endpoint_node.text = email
                party_node.insert(0, endpoint_node)
        elif self._ubl_is_norm_fr():
            adresse_electronique = partner.commercial_partner_id.electronic_address
            if adresse_electronique:
                endpoint_node = etree.Element(cbc + "EndpointID")
                endpoint_node.set("schemeID", "0225")
                endpoint_node.text = adresse_electronique
                party_node.insert(0, endpoint_node)
        else:
            email = partner.email
            if email:
                endpoint_node = etree.Element(cbc + "EndpointID")
                endpoint_node.set("schemeID", "EM")
                endpoint_node.text = email
                party_node.insert(0, endpoint_node)
        
        siren = partner.commercial_partner_id.siren or partner.siren
        if siren:
            party_legal_entity = party_node.find(cac + 'PartyLegalEntity')
            if party_legal_entity is not None:
                company_id_node = party_legal_entity.find(cbc + 'CompanyID')
                if company_id_node is not None:
                    company_id_node.set('schemeID', '0002')
                    company_id_node.text = siren
                else:
                    children = list(party_legal_entity)
                    registration_name_tag = cbc + 'RegistrationName'
                    insert_index = 0
                    for i, child in enumerate(children):
                        if child.tag == registration_name_tag:
                            insert_index = i + 1
                            break

                    company_id_node = etree.Element(cbc + 'CompanyID')
                    company_id_node.set('schemeID', '0002')
                    company_id_node.text = siren
                    party_legal_entity.insert(insert_index, company_id_node)

        return customer_party_root
    
    def _ubl_add_supplier_party(
        self, partner, company, node_name, parent_node, ns, version='2.1'
    ):
        supplier_party_root = super()._ubl_add_supplier_party(
            partner, company, node_name, parent_node, ns, version=version
        )

        cac = ns['cac']
        cbc = ns['cbc']

        party_node = supplier_party_root.find(cac + 'Party')
        if party_node is None:
            return supplier_party_root

        website_node = party_node.find(cbc + 'WebsiteURI')
        if website_node is not None:
            party_node.remove(website_node)

        if self._ubl_is_norm_fr():
            language_node = party_node.find(cac + 'Language')
            if language_node is not None:
                party_node.remove(language_node)

        electronic_address = self.company_id.get_electronic_address()
        if electronic_address:
            endpoint_node = etree.Element(cbc + 'EndpointID')
            endpoint_node.set('schemeID', '0225')
            endpoint_node.text = electronic_address
            party_node.insert(0, endpoint_node)

        siren = self.company_id.siren or self.company_id.partner_id.siren
        if siren:
            party_legal_entity = party_node.find(cac + 'PartyLegalEntity')
            if party_legal_entity is not None:
                company_id_node = party_legal_entity.find(cbc + 'CompanyID')
                if company_id_node is not None:
                    company_id_node.set('schemeID', '0002')
                    company_id_node.text = siren
                else:
                    children = list(party_legal_entity)
                    registration_name_tag = cbc + 'RegistrationName'
                    insert_index = 0
                    for i, child in enumerate(children):
                        if child.tag == registration_name_tag:
                            insert_index = i + 1
                            break

                    company_id_node = etree.Element(cbc + 'CompanyID')
                    company_id_node.set('schemeID', '0002')
                    company_id_node.text = siren
                    party_legal_entity.insert(insert_index, company_id_node)

        return supplier_party_root
    
    def _ubl_add_tax_category(
    self, tax, parent_node, ns, node_name='TaxCategory', version='2.1'
    ):
        super()._ubl_add_tax_category(
            tax, parent_node, ns, node_name=node_name, version=version
        )

        cac = ns['cac']
        cbc = ns['cbc']

        tax_category_node = parent_node.find(cac + node_name)
        if tax_category_node is None:
            return

        tax_id_node = tax_category_node.find(cbc + 'ID')
        if tax_id_node is not None and tax_id_node.text == 'AC':
            tax_id_node.text = 'S'
        
        if node_name != 'TaxCategory':
            return
        if tax.unece_categ_code != 'E':
            return
        
        vatex = self.partner_id.commercial_partner_id.vatex
        if vatex:
            sequence = [
                cbc + 'ID',
                cbc + 'Name',
                cbc + 'Percent',
                cbc + 'BaseUnitMeasure',
                cbc + 'PerUnitAmount',
                cbc + 'TaxExemptionReasonCode',
                cbc + 'TaxExemptionReason',
                cbc + 'TierRange',
                cbc + 'TierRatePercent',
                cbc + 'TaxScheme',
            ]
            target_pos = sequence.index(cbc + 'TaxExemptionReasonCode')

            children = list(tax_category_node)
            insert_at = len(children)
            for i, child in enumerate(children):
                if child.tag in sequence and sequence.index(child.tag) >= target_pos:
                    insert_at = i
                    break

            exemption_node = etree.Element(cbc + 'TaxExemptionReasonCode')
            exemption_node.text = vatex
            tax_category_node.insert(insert_at, exemption_node)
    
    def _ubl_add_tax_scheme(self, tax_scheme_dict, parent_node, ns, version='2.1'):
        super()._ubl_add_tax_scheme(tax_scheme_dict, parent_node, ns, version=version)

        cac = ns['cac']
        cbc = ns['cbc']

        tax_scheme_node = parent_node.find(cac + 'TaxScheme')
        if tax_scheme_node is None:
            return

        tax_scheme_id_node = tax_scheme_node.find(cbc + 'ID')
        if tax_scheme_id_node is not None:
            tax_scheme_id_node.attrib.pop('schemeID', None)
            tax_scheme_id_node.attrib.pop('schemeAgencyID', None)
            
    def generate_invoice_ubl_xml_etree(self, version='2.1'):
        xml_root = super().generate_invoice_ubl_xml_etree(version=version)

        if self.move_type == 'out_refund':
            self._ubl_add_billing_reference(xml_root, version=version)

        return xml_root

    def _ubl_add_billing_reference(self, parent_node, version='2.1'):
        reversed_entry = self.reversed_entry_id
        if not reversed_entry:
            return

        nsmap = parent_node.nsmap
        cac = '{%s}' % nsmap.get('cac', 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2')
        cbc = '{%s}' % nsmap.get('cbc', 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2')

        billing_ref = etree.Element(cac + 'BillingReference')
        invoice_doc_ref = etree.SubElement(billing_ref, cac + 'InvoiceDocumentReference')

        ref_id = etree.SubElement(invoice_doc_ref, cbc + 'ID')
        ref_id.text = reversed_entry.name

        if reversed_entry.invoice_date:
            ref_date = etree.SubElement(invoice_doc_ref, cbc + 'IssueDate')
            ref_date.text = reversed_entry.invoice_date.strftime('%Y-%m-%d')

        correct_order = [
            cac + 'OrderReference',
            cac + 'BillingReference',
            cac + 'DespatchDocumentReference',
            cac + 'ReceiptDocumentReference',
            cac + 'ContractDocumentReference',
            cac + 'AdditionalDocumentReference',
            cac + 'AccountingSupplierParty',
        ]

        children = list(parent_node)
        insert_at = len(children)
        for i, child in enumerate(children):
            if child.tag in correct_order[correct_order.index(cac + 'BillingReference'):]:
                insert_at = i
                break

        parent_node.insert(insert_at, billing_ref)
    
    def _ubl_add_invoice_line_discount(
    self, xml_root, iline, base_price, base_qty, ns, version="2.1"
    ):
        super()._ubl_add_invoice_line_discount(
            xml_root, iline, base_price, base_qty, ns, version=version
        )

        cac = ns['cac']
        cbc = ns['cbc']

        allowance_nodes = xml_root.findall(cac + 'AllowanceCharge')
        if not allowance_nodes:
            return

        last_allowance = allowance_nodes[-1]

        amount_node = last_allowance.find(cbc + 'Amount')
        if amount_node is not None:
            current_value = float(amount_node.text)
            amount_node.text = "%.2f" % round(current_value, 2)

    # ------------------------------------------------------------------
    # UBL - French standard (norme FR)
    # Triggered by the "Generate UBL XML File (FR)" button through the
    # 'ubl_norm_fr' context key. Differences with the standard generation:
    #   - all invoice taxes are declared as VAT: no document level
    #     AllowanceCharge (ABK), TaxTotal/LegalMonetaryTotal amounts fixed
    #   - ChargeTotalAmount always present
    #   - no Language block on the supplier party
    #   - customer EndpointID depends on the PF code (#BAR# note):
    #     B2BINT / B2C -> invoicing contact email (schemeID EM)
    #     otherwise (B2B) -> electronic address (schemeID 0225)
    #   - ClassifiedTaxCategory added on each invoice line
    # ------------------------------------------------------------------

    def _ubl_is_norm_fr(self):
        return bool(self.env.context.get('ubl_norm_fr'))

    @api.depends('currency_id')
    def _compute_is_ubl_norm_fr(self):
        # EUR invoices -> UBL EUR (French standard), other currencies -> UBL GBP
        eur = self.env.ref('base.EUR')
        for move in self:
            move.is_ubl_norm_fr = move.currency_id == eur

    def attach_ubl_fr_xml_file_button(self):
        return self.with_context(ubl_norm_fr=True).attach_ubl_xml_file_button()

    def _ubl_get_invoice_vat_exclusive_amount(self):
        if self._ubl_is_norm_fr():
            return self.amount_untaxed
        return super()._ubl_get_invoice_vat_exclusive_amount()

    def _ubl_get_invoice_vat_amount(self):
        if self._ubl_is_norm_fr():
            return self.amount_tax
        return super()._ubl_get_invoice_vat_amount()

    def _ubl_get_charge_total_amount(self):
        if self._ubl_is_norm_fr():
            return 0.0
        return super()._ubl_get_charge_total_amount()

    def _ubl_fr_add_tax_total(self, xml_root, ns, version="2.1"):
        cur_name = self.currency_id.name
        prec = self.currency_id.decimal_places

        tax_lines = {}
        for tline in self.line_ids:
            sign = 1 if tline.is_refund else -1
            if tline.tax_line_id:
                tax_lines.setdefault(tline.tax_line_id, {"base": 0.0, "amount": 0.0})
                tax_lines[tline.tax_line_id]["base"] += tline.tax_base_amount
                tax_lines[tline.tax_line_id]["amount"] += sign * tline.balance
            elif tline.tax_ids:
                # In case there are no declared (tag) repartition lines
                for tax in tline.tax_ids:
                    if not tline.is_refund and tax.invoice_repartition_line_ids.tag_ids:
                        continue
                    if tline.is_refund and tax.refund_repartition_line_ids.tag_ids:
                        continue
                    tax_lines.setdefault(tax, {"base": 0.0, "amount": 0.0})
                    tax_lines[tax]["base"] += sign * tline.balance

        tax_total_node = etree.SubElement(xml_root, ns["cac"] + "TaxTotal")
        tax_amount_node = etree.SubElement(
            tax_total_node, ns["cbc"] + "TaxAmount", currencyID=cur_name
        )
        tax_amount_node.text = "%0.*f" % (prec, self._ubl_get_invoice_vat_amount())
        for tax, amounts in tax_lines.items():
            self._ubl_add_tax_subtotal(
                amounts["base"],
                amounts["amount"],
                tax,
                cur_name,
                tax_total_node,
                ns,
                version=version,
            )

    def _ubl_add_legal_monetary_total(self, parent_node, ns, version="2.1"):
        super()._ubl_add_legal_monetary_total(parent_node, ns, version=version)
        if not self._ubl_is_norm_fr():
            return

        cac = ns['cac']
        cbc = ns['cbc']

        monetary_total = parent_node.findall(cac + 'LegalMonetaryTotal')[-1]
        if monetary_total.find(cbc + 'ChargeTotalAmount') is not None:
            return
        charge_total_node = etree.Element(
            cbc + 'ChargeTotalAmount', currencyID=self.currency_id.name
        )
        charge_total_node.text = "%0.*f" % (self.currency_id.decimal_places, 0.0)
        prepaid_node = monetary_total.find(cbc + 'PrepaidAmount')
        if prepaid_node is not None:
            prepaid_node.addprevious(charge_total_node)
        else:
            monetary_total.append(charge_total_node)

    def _ubl_add_invoice_line(self, parent_node, iline, line_number, ns, version="2.1"):
        if not self._ubl_is_norm_fr():
            return super()._ubl_add_invoice_line(
                parent_node, iline, line_number, ns, version=version
            )

        # Line taxes are added below from iline.tax_ids (instead of the
        # product taxes filtered on UNECE type VAT)
        super(AccountMove, self.with_context(ubl_add_item__skip_taxes=True))._ubl_add_invoice_line(
            parent_node, iline, line_number, ns, version=version
        )

        cac = ns['cac']
        item_node = parent_node[-1].find(cac + 'Item')
        if item_node is None or not iline.tax_ids:
            return

        # ClassifiedTaxCategory must be placed before these Item children
        following_tags = [cac + tag for tag in (
            'AdditionalItemProperty',
            'ManufacturerParty',
            'InformationContentProviderParty',
            'OriginAddress',
            'ItemInstance',
            'Certificate',
            'Dimension',
        )]
        following_nodes = [c for c in item_node if c.tag in following_tags]
        for node in following_nodes:
            item_node.remove(node)
        for tax in iline.tax_ids:
            self._ubl_add_tax_category(
                tax, item_node, ns, node_name='ClassifiedTaxCategory', version=version
            )
        for node in following_nodes:
            item_node.append(node)