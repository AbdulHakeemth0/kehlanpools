from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_amc_product = fields.Boolean(string="Is AMC Product")
    is_discount_product = fields.Boolean(string="Is Discount Product", default=False)
    
class ProductProduct(models.Model):
    _inherit = "product.product"
    
    is_discount_product = fields.Boolean(string="Is Discount Product", related='product_tmpl_id.is_discount_product', store=True)
