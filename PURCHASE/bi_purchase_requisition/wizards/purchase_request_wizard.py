from odoo import fields, models, api, _
from odoo.exceptions import UserError  

class PurchaseRequestWizard(models.TransientModel):
    _name = "purchase.request.wizard"
    _description = "Purchase Request Wizard"
    
    partner_ref = fields.Char('Subject', copy=False,required = True,
                              help="Reference of the sales order or bid sent by the vendor. "
                              "It's used to do the matching when you receive the "
                              "products as this reference is usually written on the "
                              "delivery order sent by your vendor.")
    date_order = fields.Datetime('PR Date', required=True,
                                help="Depicts the date where the Quotation should be validated and converted into a purchase order.") 
    date_end = fields.Datetime(string='Expected Order')

    requisition_wiz_line_ids = fields.One2many('purchase.request.wizard.line', 'request_wiz_id', string='Product Details', copy=True)
   
    request_id = fields.Many2one('purchase.request',string="Request id")
    m_number = fields.Char(string="M-number")
    job_number = fields.Many2one("sale.order", string="Job number")
   
    def create_purchase_requisition(self):
        line_list = []
        for rec in self.requisition_wiz_line_ids:
            line_list.append(
                (
                    0,
                    0,
                    {
                        "name": rec.name,
                        "product_qty": rec.product_qty,
                        "price_unit": rec.price_unit,
                        "price_subtotal": rec.price_subtotal,
                        # "currency_id": rec.currency_id,

                    },
                )
            )
            
        values = {
            "partner_ref": self.partner_ref,
            "pr_approved_line": line_list,
            "date_order":self.date_order,
            "date_end":self.date_end,
            "m_number" : self.m_number,
            "job_number" : self.job_number.id,
        }
        requisition = self.env['purchase.requisition.new'].create(values)
        # requisition.button_submit()
        request = self.env['purchase.request'].browse(self.request_id.id)
        request.state = 'in_progress'
        request.requisition_id = requisition
        return {
        'type': 'ir.actions.client',
        'tag': 'reload',
        }
    
class PurchaseRequestWizardLine(models.TransientModel):
    _name = "purchase.request.wizard.line"
    _description = "Purchase Request Wizard Line"
    
    request_wiz_id = fields.Many2one('purchase.request.wizard',string="Request id")
    name = fields.Char(string = "Description") 
    product_qty = fields.Float(string = "Quantity")
    price_unit = fields.Float(string = "Unit Price")
    price_subtotal = fields.Monetary(string = "Subtotal", store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    