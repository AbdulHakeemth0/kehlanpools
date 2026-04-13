from odoo import api, fields, models, _
from odoo.exceptions import UserError


class Project(models.Model):
    _inherit = 'project.project'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order',store=True)
    order_id = fields.Many2one('sale.order',string="Order")
    is_field_service = fields.Boolean(string="Is Field Service")


