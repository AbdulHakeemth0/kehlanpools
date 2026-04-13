from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    joining_date = fields.Date(string="Joining Date",tracking=True)
    is_early_leave_app = fields.Boolean(string="Early Annual Leave Applicable")

   