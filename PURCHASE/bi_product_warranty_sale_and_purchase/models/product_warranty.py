from odoo import models, fields, api 
from datetime import datetime

class ProductWarranty(models.Model):
    _name = "product.warranty"
    _rec_name = "product_id"
    _description = "Product Warranty"
    
    
    product_id = fields.Many2one('product.product',string ="Product")
    lot_id = fields.Many2one('stock.lot',string = "Lot")
    # batch_id = fields.Many2one('batch.serial','Batch', readonly=True, related='lot_id.batch_no_id',store = True)
    account_move_ids = fields.Many2many('account.move',string = "Bill",compute = "_compute_product_bill")
    move_line_id = fields.Many2one('stock.move.line',string = "Stock Move")
    picking_id = fields.Many2one('stock.picking',string = "Picking")
    vendor_id = fields.Many2one('res.partner')
    purchase_date = fields.Date(string = "Purchase date")
    sale_date = fields.Date(string = "Sale date")
    warranty_start = fields.Date(string = "Warranty start")
    warranty_left = fields.Integer(string = "Remaining days", compute = "_compute_warranty_left")
    warranty_end = fields.Date(string = "Warranty End")
    picking_type = fields.Selection(selection = [('outgoing','Outgoing'),('incoming','Incoming')])
    sale_id = fields.Many2one('sale.order', string = "Sale order")
    purchase_id = fields.Many2one('purchase.order', string = "Purchase order")
    current_date = fields.Date(string = "Current Date", compute = "_compute_current_date")
    
    def _compute_current_date(self):
        for rec in self:
            rec.current_date = datetime.now()
    
    @api.depends('current_date')
    def _compute_warranty_left(self):
        for rec in self:
            if rec.current_date and rec.warranty_end: 
                warranty_period = rec.warranty_end - rec.current_date
                rec.warranty_left = warranty_period.days
            else:
                rec.warranty_left = 0
                
    @api.depends('sale_id','purchase_id')            
    def _compute_product_bill(self):
        for rec in self:
            rec.account_move_ids = False
            if rec.purchase_id.invoice_ids:
                filtered_invoices = [invoice_id.id for invoice_id in rec.purchase_id.invoice_ids.filtered(lambda inv:inv.move_type == 'in_invoice')]
                rec.account_move_ids = [(6, 0, filtered_invoices)]
            if rec.sale_id.invoice_ids:
                filtered_invoices = [invoice_id.id for invoice_id in rec.sale_id.invoice_ids.filtered(lambda inv:inv.move_type == 'out_invoice')]
                rec.account_move_ids = [(6, 0, filtered_invoices)]
                
