from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    emp_sequence = fields.Char(string='Employee Seequence', copy=False, readonly=True, index=True, group_operator=False)

    @api.model
    def create(self, vals):
        if not vals.get('emp_sequence'):
            vals['emp_sequence'] = self.env['ir.sequence'].next_by_code('hr.employee.emp_sequence') or '/'
        return super().create(vals)
    
    def action_assign_missing_emp_codes(self):
        sequence = self.env['ir.sequence']
        for emp in self.search([('emp_sequence', '=', False)]):
            emp.emp_sequence = sequence.next_by_code('hr.employee.emp_sequence')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = args[:]
        if name:
            domain = ['|', '|',
                      ('emp_sequence', 'ilike', name),
                      ('name', 'ilike', name),
                      ('work_email', 'ilike', name)] + domain
        employees = self.search(domain, limit=limit)
        return employees.name_get()

    def name_get(self):
        result = []
        for rec in self:
            display_name = f"{rec.emp_sequence or ''} - {rec.name or ''}"
            result.append((rec.id, display_name))
        return result
    
    #Function for the server action to update the name of analytic account
    def action_update_analytic_account_name(self):
        updated_count = 0
        for employee in self:
            if not employee.emp_sequence:
                continue
            analytic_account = self.env['account.analytic.account'].search([
                # ('employee_id', '=', employee.id)
                ('name', 'ilike', employee.name)
            ], limit=1)
            if analytic_account:
                new_name = f"{employee.emp_sequence} - {employee.name}"
                if analytic_account.name != new_name:
                    analytic_account.write({'name': new_name})
                    updated_count += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Update Complete",
                "message": f"{updated_count} analytic account(s) renamed.",
                "type": "success",
                "sticky": False,
            }
        }