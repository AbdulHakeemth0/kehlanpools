from odoo import models, fields, api,_
from odoo.exceptions import UserError
from datetime import timedelta


class HrLeave(models.Model):
    _inherit = 'hr.leave'
    
    child_birth_date = fields.Date(string="Child Birth Date")
    is_child_alive = fields.Boolean(string="Is Child Alive?", default=True)
    is_paternity_leave = fields.Boolean(string="Is Paternity Leave", related="holiday_status_id.is_paternity_leave")
    is_annual_leave = fields.Boolean(string="Is Annual Leave", related="holiday_status_id.is_annual_leave")

    @api.constrains('employee_id', 'holiday_status_id','duration_display')
    def _check_maternity_leave_eligibility(self):
        for leave in self:
            if leave.holiday_status_id.is_maternity_leave:
                if not leave.employee_id.gender:
                    raise UserError("Please set employee's gender.")
                if leave.holiday_status_id.is_maternity_leave and leave.employee_id.gender != 'female': 
                    raise UserError("Only female employees are eligible for Maternity Leave.")
                if leave.number_of_days > 98:
                        raise UserError(_("Maternity Leave cannot exceed 98 days. Please adjust the leave duration."))

    @api.constrains('employee_id', 'holiday_status_id', 'child_birth_date', 'is_child_alive','duration_display')
    def _check_paternity_leave_eligibility(self):
        for leave in self:
            if leave.holiday_status_id.is_paternity_leave:
                if leave.employee_id.gender != 'male':
                    raise UserError("Only male employees are eligible for Paternity Leave.")
                if not leave.is_child_alive:
                    raise UserError("Paternity Leave is only granted if the child is born alive.")
                max_valid_date = leave.child_birth_date + timedelta(days=98)
                if leave.request_date_from > max_valid_date:
                    raise UserError("Paternity Leave must be taken within 98 days of the child's birth.")
                if leave.number_of_days > 7:
                        raise UserError(_("Paternity Leave cannot exceed 7 days. Please adjust the leave duration."))
                
    @api.constrains('employee_id', 'holiday_status_id','duration_display')
    def _check_marriage_leave_eligibility(self):
        for leave in self:
            if leave.holiday_status_id.is_marriage_leave and leave.number_of_days > 3:
                raise UserError("Marriage Leave cannot exceed 3 days. Please adjust the leave duration.")
            if leave.holiday_status_id.is_marriage_leave:
                existing_leave = self.env['hr.leave'].search([
                    ('employee_id', '=', leave.employee_id.id),
                    ('holiday_status_id', '=', leave.holiday_status_id.id),
                    ('state', '=', 'validate')
                ])
                
                if existing_leave:
                    raise UserError("Marriage Leave can only be taken once throughout your service period.")