from odoo import models, api

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HrEmployee, self).create(vals_list)
        for employee in res:
            if not employee.barcode:
                employee.generate_random_barcode()
            plan = self.env['account.analytic.plan'].search([('is_employee', '=', True)], limit=1)
            analytic_name = f"{employee.emp_sequence} - {employee.name}"
            analytic_account = self.env['account.analytic.account'].create({
                    'name': analytic_name,
                    'plan_id': plan.id if plan else False,
                    'company_id': employee.company_id.id,
                })
            contract_vals = {
                    'name': f"{employee.name} Contract",
                    'employee_id': employee.id,
                    'department_id': employee.department_id.id,
                    'job_id': employee.job_id.id,
                    'wage': 0.0,
                    'date_start': employee.joining_date,
                    'company_id': employee.company_id.id,
                    'analytic_account_id' : analytic_account.id,  
                }
            self.env['hr.contract'].sudo().create(contract_vals)
        return res
