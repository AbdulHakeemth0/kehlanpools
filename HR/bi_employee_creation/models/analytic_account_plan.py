from odoo import models, fields

class AccountAnalyticPlan(models.Model):
    _inherit = 'account.analytic.plan'

    is_employee = fields.Boolean(string="Is Employee", default=False)
