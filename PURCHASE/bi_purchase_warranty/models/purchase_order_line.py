from odoo import models, fields,api


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    number_of_warranty = fields.Float(string="Warranty", copy=False)
    warranty_type = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Warranty Period", copy=False)
    
    discount_amount = fields.Monetary(string="Discount Amount", store=True)

    @api.onchange('product_qty','price_unit','discount_amount')
    def _onchange_discount_percentage(self):
        """
        Updates the discount amount when the discount percentage changes.
        """
        for line in self:
            if line.discount_amount:
                total = line.product_qty * line.price_unit
                if total != 0:
                    line.discount = (line.discount_amount / total) * 100
            elif line.discount_amount == 0.0:
                line.discount = 0.0
