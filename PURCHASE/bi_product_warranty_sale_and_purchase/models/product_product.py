from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit ="product.product"
    
    
    purchase_warranty = fields.Float(string = "Purchase warranty", compute="compute_warranty",store = True)
    purchase_warranty_period = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Purchase Warranty Period", copy=False, compute="compute_warranty",store = True)
    sale_warranty = fields.Float(string = "Sale warranty",compute="compute_warranty",store = True)
    sale_warranty_period = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Sale Warranty Period", copy=False, compute="compute_warranty",store = True)

    # Civil warranty fields
    civil_warranty = fields.Float(string="Civil Warranty", compute="compute_warranty", store=True)
    civil_warranty_period = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Civil Warranty Period", copy=False, compute="compute_warranty", store=True)

    @api.depends('product_tmpl_id.purchase_warranty', 'product_tmpl_id.purchase_warranty_period', 'product_tmpl_id.sale_warranty', 'product_tmpl_id.sale_warranty_period','product_tmpl_id.civil_warranty', 'product_tmpl_id.civil_warranty_period')
    def compute_warranty(self):
        for rec in self:
            if rec.product_tmpl_id.purchase_warranty:
                rec.purchase_warranty = rec.product_tmpl_id.purchase_warranty
            else:
                rec.purchase_warranty = False
            if rec.product_tmpl_id.purchase_warranty_period:
                rec.purchase_warranty_period = rec.product_tmpl_id.purchase_warranty_period
            else:
                rec.purchase_warranty_period = False
                
            if rec.product_tmpl_id.sale_warranty:
                rec.sale_warranty = rec.product_tmpl_id.sale_warranty
            else:
                rec.sale_warranty = False
            if rec.product_tmpl_id.sale_warranty_period:
                rec.sale_warranty_period = rec.product_tmpl_id.sale_warranty_period
            else:
                rec.sale_warranty_period = False
            if rec.product_tmpl_id.civil_warranty:
                rec.civil_warranty = rec.product_tmpl_id.civil_warranty
            else:
                rec.civil_warranty = False
            if rec.product_tmpl_id.civil_warranty_period:
                rec.civil_warranty_period = rec.product_tmpl_id.civil_warranty_period
            else:
                rec.civil_warranty = False

                