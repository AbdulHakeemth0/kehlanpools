from odoo import models, fields, api,_
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
import re
from odoo.tools.float_utils import float_round, float_compare


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    leave_salary_type = fields.Selection([('partial','Partial'),('full','Full')],tracking=True)
    annual_leave_salary = fields.Float("Annual leave salary",tracking=True)
    is_leave_annual = fields.Boolean(string="Annual Leave", related="holiday_status_id.is_annual_leave")
    is_full_leave_salary = fields.Boolean('Full leave salary',tracking=True)
    is_partial_leave_salary = fields.Boolean('Partial leave salary',tracking=True)

    def write(self, vals):
        today = fields.Date.today()
        for each in self:
            if each.holiday_status_id.is_annual_leave == True:
                if not each.employee_id.is_early_leave_app:
                    if each.employee_id.joining_date:
                        contract_year = each.employee_id.joining_date + relativedelta(months=11)
                        if each.employee_id.job_id.is_staff: 
                            if relativedelta(today, contract_year).months + (relativedelta(today, contract_year).years * 12) < 11:
                                raise UserError(each.env._("You are not eligible to apply the 'Annual leave'."))
                        elif each.employee_id.job_id.is_technician:
                            if relativedelta(today, contract_year).months + (relativedelta(today, contract_year).years * 12) < 23:
                                raise UserError(each.env._("You are not eligible to apply the 'Annual leave'."))
                    else:
                        raise UserError(each.env._("Please add joining date for this Employee."))
        return super().write(vals)

    def leave_salary_action(self):
        total_wage = self.employee_id.contract_id.wage + self.employee_id.contract_id.house_alw + self.employee_id.contract_id.travel_alw + self.employee_id.contract_id.meal_alw + self.employee_id.contract_id.fuel_alw + self.employee_id.contract_id.other_alw
        per_day_wage = total_wage/365
        leave_salary = per_day_wage * self.number_of_days 
        self.annual_leave_salary = leave_salary
        # context = {
        #     'default_hr_leave_id': self.id,
        # }
        # return {
        #     'name': 'Annual Leave Salary',
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'leave.salary.wizard',
        #     'view_mode': 'form',
        #     'target': 'new',
        #     'context' : context
        # }
    
    # overrided the duration in time off
    @api.depends('number_of_hours', 'number_of_days', 'leave_type_request_unit')
    def _compute_duration_display(self):
        for leave in self:
            if leave.holiday_status_id.is_annual_leave:
                leave.duration_display = (leave.date_to-leave.date_from).days + 1 
            else:
                duration = leave.number_of_days
                unit = _('days')
                display = "%g %s" % (float_round(duration, precision_digits=2), unit)
                if leave.leave_type_request_unit == "hour":
                    hours, minutes = divmod(abs(leave.number_of_hours) * 60, 60)
                    minutes = round(minutes)
                    if minutes == 60:
                        minutes = 0
                        hours += 1
                    duration = '%d:%02d' % (hours, minutes)
                    unit = _("hours")
                    display = f"{duration} {unit}"
                leave.duration_display = display
