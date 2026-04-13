from odoo import models, fields, api 
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta

class StockPicking(models.Model):
    
    _inherit = "stock.picking"
    
    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        for rec in self:
            if rec.picking_type_code != 'internal':
                for line in rec.move_line_ids :
                    warranty_start = ""
                    warranty_end = ""
                    number_of_warranty = line.move_id.warranty
                    warranty_type = line.move_id.warranty_type
                    warranty_start = datetime.now()
                    if number_of_warranty and warranty_type and warranty_start:
                        if rec.picking_type_code == 'incoming' and line.move_id.purchase_line_id and line.move_id.warranty and line.move_id.warranty_type:
                            picking_type = 'incoming'
                            # warranty_start = line.picking_id.date_done
                            if warranty_type == 'years':
                                warranty_end = warranty_start + relativedelta(years=int(number_of_warranty))
                            if warranty_type == 'months':
                                warranty_end = warranty_start + relativedelta(months=int(number_of_warranty))
                            if warranty_type == 'days':
                                warranty_end = warranty_start + timedelta(days=int(number_of_warranty))
                            if not line.product_id.purchase_warranty:
                                if line.move_id.warranty:
                                    line.product_id.purchase_warranty = line.move_id.warranty
                                    line.product_id.product_tmpl_id.purchase_warranty = line.move_id.warranty
                                if line.move_id.warranty_type:
                                    line.product_id.purchase_warranty_period = line.move_id.warranty_type
                                    line.product_id.product_tmpl_id.purchase_warranty_period = line.move_id.warranty_type    
                            vals = {
                                'product_id':line.product_id.id,
                                'lot_id':line.lot_id.id,
                                # 'batch_id':line.lot_id.batch_no_id.id,
                                # 'account_move_id':account_move,
                                'move_line_id':line.id,
                                'picking_id':rec.id,
                                'vendor_id':rec.partner_id.id,
                                'purchase_date':rec.purchase_id.date_approve,
                                'sale_date':rec.sale_id.date_order,
                                'warranty_start':warranty_start and warranty_start or False,
                                'warranty_end':warranty_end and warranty_end,
                                'picking_type':picking_type,
                                'purchase_id':rec.purchase_id.id,
                                'sale_id':rec.sale_id.id
                                }
                            if vals:
                                self.env["product.warranty"].create(vals)  
                        if rec.picking_type_code == 'outgoing' and line.move_id.sale_line_id and line.move_id.warranty and line.move_id.warranty_type:
                            picking_type = 'outgoing'
                            # warranty_start = line.picking_id.date_done
                            if warranty_type == 'years':
                                warranty_end = warranty_start + relativedelta(years=int(number_of_warranty))
                            if warranty_type == 'months':
                                warranty_end = warranty_start + relativedelta(months=int(number_of_warranty))
                            if warranty_type == 'days':
                                warranty_end = warranty_start + timedelta(days=int(number_of_warranty))
                            # if not line.product_id.sale_warranty:
                            #     if line.move_id.warranty:
                            #         line.product_id.sale_warranty = line.move_id.warranty
                            #         line.product_id.product_tmpl_id.sale_warranty = line.move_id.warranty
                            #     if line.move_id.warranty_type:
                            #         line.product_id.sale_warranty_period = line.move_id.warranty_type
                            #         line.product_id.product_tmpl_id.sale_warranty_period = line.move_id.warranty_type            
                            vals = {
                                'product_id':line.product_id.id,
                                'lot_id':line.lot_id.id,
                                # 'batch_id':line.lot_id.batch_no_id.id,
                                # 'account_move_id':account_move,
                                'move_line_id':line.id,
                                'picking_id':rec.id,
                                'vendor_id':rec.partner_id.id,
                                'purchase_date':rec.purchase_id.date_approve,
                                'sale_date':rec.sale_id.date_order,
                                'warranty_start':warranty_start and warranty_start or False,
                                'warranty_end':warranty_end and warranty_end or False,
                                'picking_type':picking_type,
                                'purchase_id':rec.purchase_id.id,
                                'sale_id':rec.sale_id.id
                                }
                            if vals:
                                self.env["product.warranty"].create(vals)
        return res
        
    
    