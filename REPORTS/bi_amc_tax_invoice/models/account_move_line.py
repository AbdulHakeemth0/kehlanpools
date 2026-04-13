from odoo import models,fields


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    product_label = fields.Char(string="Description")