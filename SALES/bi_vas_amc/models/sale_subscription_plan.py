from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare

class SaleSubscriptionPlan(models.Model):
    _inherit = 'sale.subscription.plan'

    is_weekly = fields.Boolean(string='Is Weekly')
    is_monthly = fields.Boolean(string='Is Monthly')
    is_yearly = fields.Boolean(string='Is Yearly')
    is_quaterly = fields.Boolean(string='Is Quaterly')
    is_bi_yearly = fields.Boolean(string='Is Bi-Yearly')
    uom_id = fields.Many2one('uom.uom', string = 'UOM')