from odoo import models, fields, api 


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    approved_by = fields.Many2one("res.users", string="Approved By", copy=False)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for order in self:
            for line in order.order_line:
                for move in line.move_ids:
                    move.warranty = line.number_of_warranty
                    move.warranty_type = line.warranty_type
            order.approved_by = self.env.user.id
        return res

    def button_cancel(self):
        for line in self.material_req_id.order_line:
                line.product_qty
                if line.qty_done:
                    line.product_qty  = line.product_qty + line.qty_done
                    line.qty_done=0            
        return super().button_cancel()
    

class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"
    
    
    @api.onchange('product_id')
    def product_warranty_fetch(self):
        for rec in self:
            if rec.product_id.purchase_warranty and rec.product_id.purchase_warranty_period:
                rec.number_of_warranty = rec.product_id.purchase_warranty
                rec.warranty_type = rec.product_id.purchase_warranty_period
                
        