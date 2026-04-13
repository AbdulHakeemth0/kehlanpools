from odoo import models, fields, api 


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            if rec.purchase_id:
               rec.purchase_id.bi_purchase_quotation_id.bi_purchase_id.requisition_id.write({"status_po": "goods_received"}) 
        return res
    
    
    # @api.model_create_multi
    # def create(self, vals_list):
       
    #     for vals in vals_list:
    #         picking_id = vals.get('picking_type_id')
    #         picking = self.env['stock.picking.type'].search([('id','=',picking_id)])
    #         if picking.code == 'incoming':
    #             vals['name'] = self.env['ir.sequence'].next_by_code('stock.picking') or '/'
                
    #         res = super(StockPicking, self).create(vals)                              
                  
    #     return res                

    
    