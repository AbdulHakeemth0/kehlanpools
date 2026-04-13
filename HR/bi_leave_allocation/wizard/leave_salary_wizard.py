from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LeaveSalaryWizard(models.TransientModel):
    _name = 'leave.salary.wizard'
    _description = 'Leave Salary'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    leave_salary_type = fields.Selection([('partial','Partial'),('full','Full')],tracking=True,required=True)
    leave_salary_annual = fields.Float(string='Leave Salary Amount',tracking=True)
    leave_date_from = fields.Date(string='Leave Start Date', tracking=True)
    leave_date_to = fields.Date(string='Leave End Date', tracking=True)
    hr_leave_id = fields.Many2one("hr.leave",string='Time off',tracking=True)

    @api.onchange('leave_date_from', 'leave_date_to', 'leave_salary_type')
    def _onchange_dates(self):
        for rec in self:
            if self.leave_salary_type == 'partial':
                if self.leave_date_from and self.leave_date_to:
                    leave_duration = (self.leave_date_to - self.leave_date_from).days+1
                    leave_type = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)],limit=1)
                    allocation = self.env['hr.leave.allocation'].search([
                        ('employee_id', '=', self.hr_leave_id.employee_id.id),
                        ('holiday_status_id','=',self.hr_leave_id.holiday_status_id.id),
                        ('state','=','validate')
                    ],limit=1)
                    per_day_wage = self.hr_leave_id.employee_id.contract_id.wage / 30
                    allocated_days = allocation.number_of_days_display if allocation else 0
                    if allocated_days:
                        total_days_for_encashment = allocated_days - leave_duration
                        leave_salary = total_days_for_encashment * per_day_wage
                    else:
                        leave_salary = 0

                    rec.leave_salary_annual = leave_salary
            elif self.leave_salary_type == 'full':
                per_day_wage = self.hr_leave_id.employee_id.contract_id.wage / 30
                leave_salary = per_day_wage * 30
                rec.leave_salary_annual = leave_salary



    @api.constrains('leave_date_from', 'leave_date_to', 'leave_salary_type')
    def _check_dates_required(self):
        for rec in self:
            if rec.leave_salary_type == 'partial':
                if not rec.leave_date_from or not rec.leave_date_to:
                    raise ValidationError(
                        "For 'Partial' Leave Salary, both Leave Start Date and Leave End Date are required."
                    )

    def action_leave_salary(self):
        for wizard in self:
            wizard.hr_leave_id.is_full_leave_salary = False
            wizard.hr_leave_id.is_partial_leave_salary = False
            if wizard.hr_leave_id:
                if wizard.leave_salary_type == 'full':
                    wizard.hr_leave_id.annual_leave_salary = wizard.leave_salary_annual
                    wizard.hr_leave_id.leave_salary_type = wizard.leave_salary_type
                    wizard.hr_leave_id.is_full_leave_salary = True
                elif wizard.leave_salary_type == 'partial':
                    if wizard.leave_date_from and wizard.leave_date_to:
                        wizard.hr_leave_id.write({
                            "request_date_from": wizard.leave_date_from,
                            "request_date_to": wizard.leave_date_to,
                            })
                    wizard.hr_leave_id.annual_leave_salary = wizard.leave_salary_annual
                    wizard.hr_leave_id.leave_salary_type = wizard.leave_salary_type
                    wizard.hr_leave_id.is_partial_leave_salary = True
                    # wizard.hr_leave_id.write({
                    #     "request_date_from": wizard.leave_date_from,
                    #     "request_date_to": wizard.leave_date_to,
                    # })
