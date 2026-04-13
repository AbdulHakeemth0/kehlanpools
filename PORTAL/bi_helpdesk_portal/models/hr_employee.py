from odoo import fields,models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_team_lead = fields.Boolean(string="Is Team Lead")