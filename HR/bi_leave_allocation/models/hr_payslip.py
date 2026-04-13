from odoo import models, fields, api, _
from datetime import datetime

class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')          
    def _compute_input_line_ids(self):
        """ Fetches the annual leave salary from hr.leave and passes it to the payslip inputs """
        res = super()._compute_input_line_ids()

        for rec in self:
            leave_type = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)], limit=1)
            if not leave_type:
                continue  # Skip if no annual leave type is found

            # Fetch leaves within the payslip period that are validated
            leaves = self.env['hr.leave'].search([
                ('employee_id','=', self.employee_id.id),
                ('holiday_status_id','=', leave_type.id),
                ('state', '=', 'validate')])

            if leaves:
                total_leave_salary = sum(leaves.mapped("annual_leave_salary"))

                # Ensure the input type exists
                rev_input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', "ASL")], limit=1)
                if not rev_input_type_id:
                    continue  # Skip if no input type is found

                # Ensure ALS rule exists in the salary structure
                existing_rule = rec.struct_id.rule_ids.filtered(lambda x: x.code == "ASL")
                if existing_rule:
                    existing_line = rec.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)

                    if existing_line:
                        existing_line.write({
                            'amount': total_leave_salary,
                            'name': "Annual Leave Salary"
                        })
                    else:
                        to_add_vals = {
                            'amount': total_leave_salary,
                            'input_type_id': rev_input_type_id.id,
                            'name': "Annual Leave Salary"
                        }
                        rec.input_line_ids = [(0, 0, to_add_vals)]  # Append safely

        return res