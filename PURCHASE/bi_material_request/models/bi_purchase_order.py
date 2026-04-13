from odoo import fields, models

class BiPurchaseOrder(models.Model):
    _inherit = 'bi.purchase.order'

    prepared_by = fields.Many2one('res.users', string='Prepared By')
    approved_by = fields.Many2one('res.users', string='Approved By')
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company.id)