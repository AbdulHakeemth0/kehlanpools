from odoo import models, fields, api
from datetime import datetime

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')          
    def _compute_input_line_ids(self):
        """ Override to compute sick leave deductions based on Oman labor law. """
        res = super(HrPayslip, self)._compute_input_line_ids()

        for payslip in self:
            if not payslip.employee_id or not payslip.struct_id:
                continue
            
            employee = payslip.employee_id
            contract = payslip.contract_id
            basic_salary = contract.wage if contract else 0

            sick_leave_type = self.env['hr.leave.type'].search([('is_sick_leave_oman', '=', True)], limit=1)
            if not sick_leave_type:
                continue

            # Fetch sick leaves for the current year
            year_start_date = datetime(datetime.today().year, 1, 1).date()
            monthly_sick_leave = self.env['hr.leave'].search([
                                                            ('employee_id','=', employee.id),
                                                            ('holiday_status_id','=', sick_leave_type.id),
                                                            ('state', '=', 'validate'),
                                                            ('request_date_from','>=',payslip.date_from),
                                                            ('request_date_to','<=',payslip.date_to)])
            sick_leaves = self.env['hr.leave'].search([
                ('holiday_status_id', '=', sick_leave_type.id),
                ('employee_id', '=', employee.id),
                ('request_date_from', '>=', year_start_date),
                ('state', '=', 'validate'),
            ])

            # Fetch previously issued sick leaves before this month
            issued_sick_leaves = self.env['hr.leave'].search([
                ('holiday_status_id', '=', sick_leave_type.id),
                ('employee_id', '=', employee.id),
                ('request_date_from', '>=', year_start_date),
                ('request_date_to', '<', payslip.date_from),
                ('state', '=', 'validate'),
            ])
            total_sick_days = sum(sick_leaves.mapped("number_of_days"))
            previously_issued_days = sum(issued_sick_leaves.mapped("number_of_days"))
            input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', "SICK_DAYS")], limit=1)
            existing_line = payslip.input_line_ids.filtered(lambda line: line.input_type_id == input_type_id)
            leave_amount = 0
            if monthly_sick_leave:
                if total_sick_days > 21:
                    if total_sick_days <= 35:
                        deduction_days = total_sick_days - max(previously_issued_days, 21)
                        leave_amount = ((deduction_days * basic_salary) / 30) * (25 / 100)
                    elif total_sick_days > 35 and total_sick_days <= 70:
                        deduction_days = total_sick_days - previously_issued_days
                        leave_amount = ((deduction_days * basic_salary) / 30) * (50 / 100)
                    elif total_sick_days > 70 and total_sick_days <= 182:
                        deduction_days = total_sick_days - previously_issued_days
                        leave_amount = ((deduction_days * basic_salary) / 30) * (65 / 100)
                    else:
                        leave_amount = basic_salary

                if total_sick_days > 0:
                    if existing_line:
                        existing_line.write({
                            'amount': leave_amount,
                            'name': "Sick Leave",
                        })
                    else:
                        input_vals = {
                            'amount': leave_amount,
                            'input_type_id': input_type_id.id,
                            'name': "Sick Leave",
                        }
                        payslip.update({'input_line_ids': [(0, 0, input_vals)]})
                else:
                    if existing_line:
                        existing_line.unlink()
            else:
                payslip.input_line_ids = [(2, line.id) for line in payslip.input_line_ids if line.input_type_id == input_type_id]
        return res
