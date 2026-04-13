from odoo import models, fields


class ProductTemplateWarranty(models.Model):
    _name = 'product.template.warranty'
    _description = 'Product Template Warranty'

    partner_id = fields.Many2one('res.partner', string="Vendor")
    number_of_warranty = fields.Float(string="Warranty")
    warranty_type = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Warranty Period")
    template_id = fields.Many2one('product.template', string="Product")
