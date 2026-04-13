from odoo import fields,models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_passi_applicable = fields.Boolean(string="Passi Commission Applicable")