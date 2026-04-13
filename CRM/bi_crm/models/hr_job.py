from odoo import models, fields

class HrJob(models.Model):
    _inherit = "hr.job"

    is_sales_executive = fields.Boolean(string="Is Sales Executive", tracking=True)
    is_sales_engineer = fields.Boolean(string="Is Sales Engineer", tracking=True)
    is_operational_manager = fields.Boolean(string="Is Operational manager", tracking=True)