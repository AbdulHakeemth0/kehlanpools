from odoo import models, fields, api, _
from datetime import date, timedelta,datetime

class HrPayslip(models.Model):
    _inherit = "hr.payslip"
    
    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')          
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for each_emp in self:
            employee_id =  self.env['hr.contract'].sudo().search([('employee_id', '=', each_emp.employee_id.id),('employee_id.is_passi_applicable', '=', True)])
            if employee_id:
                employee_wage = employee_id.wage
                passi_commision_id = self.env['pasi.commission'].search([('company_id', '=', self.env.company.id)],limit=1)
                if passi_commision_id:
                    employee_deduction = passi_commision_id.employee_contribution
                    employee_contribution = employee_wage*employee_deduction/100
                    
                    employer_deduction = passi_commision_id.employer_contribution
                    employer_contributions = employee_wage*employer_deduction/100
                    
                    existing_rule = each_emp.struct_id.rule_ids.filtered(lambda x: x.code == "ECS")
                    if existing_rule:
                        rev_input_type_id = each_emp.env['hr.payslip.input.type'].search([('code', '=', "ECS")], limit=1)
                        existing_line = each_emp.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)
                        if existing_line:
                            existing_line.write({
                                'amount': employee_contribution,
                                'name': "Employer Contribution Salary"
                            })
                        else:
                            to_add_vals = {
                                'amount':employee_contribution,
                                'input_type_id': rev_input_type_id.id,
                                'name': "Employer Contribution Salary"
                            }
                            each_emp.update({
                                'input_line_ids': [(0, 0, to_add_vals)]
                            })
                    deduction_existing_rule = each_emp.struct_id.rule_ids.filtered(lambda x: x.code == "EDS")
                    if deduction_existing_rule:
                        rev_input_type_id = each_emp.env['hr.payslip.input.type'].search([('code', '=', "EDS")], limit=1)
                        existing_line = each_emp.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)
                        if existing_line:
                            existing_line.write({
                                'amount': employer_contributions,
                                'name': "Employee Deduction Salary"
                            })
                        else:
                            to_add_vals = {
                                'amount':employer_contributions,
                                'input_type_id': rev_input_type_id.id,
                                'name': "Employee Deduction Salary"
                            }
                            each_emp.update({
                                'input_line_ids': [(0, 0, to_add_vals)]
                            })
            else:
                contribution_input_type_id = each_emp.env['hr.payslip.input.type'].search([('code', '=', "ECS")], limit=1)
                contribution_existing_line = each_emp.input_line_ids.filtered(lambda line: line.input_type_id == contribution_input_type_id)
                deduction_input_type_id = each_emp.env['hr.payslip.input.type'].search([('code', '=', "EDS")], limit=1)
                deduction_existing_line = each_emp.input_line_ids.filtered(lambda line: line.input_type_id == deduction_input_type_id)
                if contribution_existing_line:
                    contribution_existing_line.unlink()
                if deduction_existing_line:
                    deduction_existing_line.unlink()
        return res