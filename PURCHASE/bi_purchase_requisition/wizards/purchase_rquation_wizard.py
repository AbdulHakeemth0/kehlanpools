from odoo import fields, models, api, _
from odoo.exceptions import UserError  

class RequisitionWizard(models.TransientModel):
    _name = "requisition.wizard"
    _description = "Requisition Wizard"
    
    partner_ids = fields.Many2many('res.partner', string="Supplier")
    # partner_domain_ids = fields.Many2many('res.partner',string = "Vendor Domain")
    # domain="[('id', 'in', rfq_id.vendor_id.ids)]"
    requisition_id = fields.Many2one('purchase.requisition.new',string="RFQ")
    requisition_wiz_line_ids = fields.One2many("requisition.wizard.line", "requisition_wiz_id", string="Agreement")
    name = fields.Text(string="Origin")
    date_end = fields.Date(string="Delivery Date")
    payment_term_id = fields.Many2one('account.payment.term', string="Payment Term")
    m_number = fields.Char(string="M-number")
    job_number = fields.Many2one("sale.order", string="Job number")


    def create_rfq(self):
        line_list = []
        for rec in self.requisition_wiz_line_ids:
            if not rec.product_id:
                raise UserError(_("Provide Product to approve Purchase Requisition")) 
            line_list.append(
                (
                    0,
                    0,
                    {
                        "product_id":rec.product_id.id,
                        "name": rec.name,
                        "product_qty": rec.product_qty,
                        "price_unit": rec.price_unit,
                        "price_subtotal": rec.price_subtotal,
                        "product_uom": rec.product_uom.id if rec.product_uom else False,
                        # "currency_id": rec.currency_id,

                    },
                )
            )
            
        values = {
            # "partner_id": self.user_id.id,
            "vendor_id":self.partner_ids.ids,
            "origin":self.name,
            "delivery_date":self.date_end,
            "payment_term_id":self.payment_term_id.id,
            "order_line": line_list,
            "requisition_id":self.requisition_id.id,
        }
        rfq_id = self.env['bi.purchase.order'].create(values)
        return {
        'type': 'ir.actions.client',
        'tag': 'reload',
        }
        # rfq_id.button_submit()
        # self.rfq_order_id = rfq_id
        # self.state = 'approved'
        # self.status_po = 'approved'
    
class RequisitionWizardLine(models.TransientModel):
    _name = "requisition.wizard.line"
    _description = "Requisition Wizard Line"
    
    requisition_wiz_id = fields.Many2one('requisition.wizard',string="Purchase id")
    product_id = fields.Many2one('product.product',string="Product")
    name = fields.Text(string="Description")
    product_qty = fields.Float(string = "Quantity")
    price_unit = fields.Float(string = "Unit Price")
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure")
    price_subtotal = fields.Float(string="Subtotal")
    # discount = fields.Float(string="Discount (%)", digits="Discount", default=0.0)
    # taxes_id = fields.Many2many("account.tax", string="Taxes", domain=[("type_tax_use", "=", "purchase")])
     
    