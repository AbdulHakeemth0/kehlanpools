from odoo import fields, models, api, _
from odoo.exceptions import UserError  

class QuotationWizard(models.TransientModel):
    _name = "quotation.wizard"
    _description = "quotation Wizard"
    
    partner_id = fields.Many2one('res.partner', string="Vendor")
    partner_domain_ids = fields.Many2many('res.partner',string = "Vendor Domain")
    # domain="[('id', 'in', rfq_id.vendor_id.ids)]"
    rfq_id = fields.Many2one('bi.purchase.order',string="RFQ")
    quotation_wiz_line_ids = fields.One2many("quotation.wizard.line", "quotation_wiz_id", string="Agreement")
    m_number = fields.Char(string="M-number")
    job_number = fields.Many2one("sale.order", string="Job number")

    def create_quotation(self):
        if self.rfq_id.state not in ['approve','purchase']:
            raise UserError(_("Please Make sure to approve RFQ to continue"))
        line_list = []
        for rec in self.quotation_wiz_line_ids:
            line_list.append(
                (
                    0,
                    0,
                    {
                        "product_id":rec.product_id.id,
                        "product_qty": rec.product_qty,
                        "product_uom":rec.product_uom.id,
                        "price_unit":rec.price_unit,
                        "taxes_id":rec.taxes_id.ids,
                        "discount":rec.discount,
                        "name":rec.name
                       
                        # "price_subtotal": rec.price_subtotal,
                        # "currency_id": rec.currency_id,

                    },
                )
            )
            
        values = {
            "partner_id": self.partner_id.id,
            "m_number":self.m_number,
            "job_number":self.job_number.id,
            "mr_remarks":self.rfq_id.notes,
            "currency_id":self.partner_id.property_purchase_currency_id.id or self.partner_id.currency_id.id or self.env.company.currency_id.id,
            # "origin":self.name,
            "date_planned":self.rfq_id.delivery_date,
            "order_line": line_list,
            # "bi_purchase_quotation_id":self.id,
            "material_req_id":self.rfq_id.id
            # "payment_term_id":self.payment_term_id,
        }
        purchase_id = self.env['purchase.order'].create(values)
        self.rfq_id.state = 'purchase'
        # rfq_id.button_submit()
        # self.purchase_id = purchase_id
        # self.state = 'purchase'
        # self.bi_purchase_id.requisition_id.write({"status_po": "purchase_order"})

        for rec in self.quotation_wiz_line_ids:
            line_list.append(
                (
                    0,
                    0,
                    {
                        "product_id":rec.product_id.id,
                        "name": rec.name,
                        "product_qty": rec.product_qty,
                        "price_unit": rec.product_id.standard_price,
                        "product_uom":rec.product_uom.id,
                        "discount":rec.discount,
                        "taxes_id":rec.taxes_id.ids,
                    },
                )
            )
            
        values = {
            "partner_id": self.partner_id.id,
            "origin":self.rfq_id.name,
            "quotation_line": line_list,
            "date_order":self.rfq_id.date_order,
            "partner_ref":self.rfq_id.partner_ref,
            "payment_term_id":self.rfq_id.payment_term_id.id,
            "bi_purchase_id":self.rfq_id.id,
        }
        quotation = self.env['bi.purchase.quotation'].create(values)
        for each in self.quotation_wiz_line_ids:
            for line in self.rfq_id.order_line:
                if line.id == each.purchase_orderline_id.id:
                    qty = line.product_qty-each.product_qty
                    line.write({'product_qty':qty,
                                'qty_done':each.product_qty})
        # quotation.confirm_quotation()
        self.rfq_id.requisition_id.write({"status_po": "quotation_confirm"})
        
        return {
        'type': 'ir.actions.client',
        'tag': 'reload',
        }
            
        # self.rfq_id.bi_purchase_quotation_id = quotation
        # self.rfq_id.state = 'purchase_quotation'
    
class QuotationWizardLine(models.TransientModel):
    _name = "quotation.wizard.line"
    _description = "quotation Wizard Line"
    
    quotation_wiz_id = fields.Many2one('quotation.wizard',string="Purchase id")
    product_id = fields.Many2one('product.product',string="Product")
    purchase_orderline_id = fields.Many2one('bi.purchase.order.line',string="purchase line")
    name = fields.Text(string="Description")
    product_qty = fields.Float(string = "Quantity")
    price_unit = fields.Float(string = "Unit Price")
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure")
    discount = fields.Float(string="Discount (%)", digits="Discount", default=0.0)
    taxes_id = fields.Many2many("account.tax", string="Taxes", domain=[("type_tax_use", "=", "purchase")])
     
    