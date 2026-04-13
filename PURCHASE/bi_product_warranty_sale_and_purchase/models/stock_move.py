from odoo import models, fields, api 

class StockMove(models.Model):
    
    _inherit = "stock.move"
    
    warranty = fields.Float(string = "Warranty",compute = "compute_warranty", store=True, readonly=False)
    warranty_type = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Warranty Period", copy=False,compute = "compute_warranty", store=True, readonly=False)

    
    
    @api.depends('picking_id', 'picking_id.move_ids.product_id')
    def compute_warranty(self):
        for line in self:
            # line.warranty = False
            # line.warranty_type = False
            if line.picking_id.picking_type_code != "internal":
                if line.purchase_line_id.number_of_warranty or line.purchase_line_id.warranty_type:
                    line.warranty = line.purchase_line_id.number_of_warranty
                    line.warranty_type = line.purchase_line_id.warranty_type
                elif line.picking_id.picking_type_code == 'incoming':
                        line.warranty = line.product_id.purchase_warranty
                        line.warranty_type = line.product_id.purchase_warranty_period
                else:
                    line.warranty = False
                    line.warranty_type = False
                if line.picking_id.picking_type_code == 'outgoing':   
                    if line.product_id.sale_warranty  or line.product_id.sale_warranty_period:
                        line.warranty = line.product_id.sale_warranty
                        line.warranty_type = line.product_id.sale_warranty_period
                    else:
                        line.warranty = False
                        line.warranty_type = False
        