from odoo import models, fields
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_id_type = fields.Selection([
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D')
    ], string="Employee Grading")

    def write(self, vals):
        res = super().write(vals)
        for employee in self:
            if 'active' in vals and vals['active'] == False:
                gratuity = self.env['gratuity.provision'].search([('employee_id', '=', employee.id)], limit=1)
                if not gratuity:
                    gratuity = self.env['gratuity.provision'].with_context(is_write = True).create({'employee_id': employee.id})
                gratuity.onchange_employee_id()
            if 'active' in vals and vals['active'] == True:
                gratuity = self.env['gratuity.provision'].search([('employee_id', '=', employee.id)])
                gratuity.unlink()
            
        return res
    
    def update_employee_timezone(self):
        for rec in self:
            rec.tz = rec.resource_calendar_id.tz
