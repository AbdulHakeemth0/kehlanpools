from odoo import models, fields, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    is_gratuity_app = fields.Boolean(string="Is Gratuity Applicable")

   