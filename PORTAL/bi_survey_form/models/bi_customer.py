from odoo import fields, models, _

class ResPartner(models.Model):
    _inherit = 'res.partner'

    way_no = fields.Text(string="Way No")

    
