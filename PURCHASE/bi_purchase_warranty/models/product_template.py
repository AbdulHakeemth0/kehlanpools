from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    template_warranty_ids = fields.One2many('product.template.warranty', 'template_id', string="Warranty")
