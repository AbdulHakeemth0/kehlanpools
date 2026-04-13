from odoo import models,fields,api
from dateutil.relativedelta import relativedelta
from odoo import Command


class HrPayslip(models.Model):
    _inherit = "hr.payslip"
    
    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')          
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for each_emp in self:
            if each_emp.employee_id and each_emp.struct_id:
                contract_id =  self.env['hr.contract'].sudo().search([('employee_id', '=', each_emp.employee_id.id)])
                if contract_id:
                    # existing_rule = each_emp.struct_id.rule_ids.filtered(lambda x: x.code == "ECS")
                    # if existing_rule:
                    request_advance_id = self.env['request.advance'].search([
                        ('employee_id','=',each_emp.employee_id.id),
                        ('state','=','approved'),
                        ('is_deduct_from_salary','=',False),
                        ('approved_date','>=',each_emp.date_from),
                        ('approved_date','<=',each_emp.date_to),
                    ])
                    rev_input_type_id = each_emp.env['hr.payslip.input.type'].search([('code', '=', "ADV100")], limit=1)
                    if request_advance_id:
                        existing_line = each_emp.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)
                        if existing_line:
                            existing_line.write({
                                'amount': sum(request_advance_id.mapped("approved_amount")),
                                'name': "Advance Salary"
                            })
                        else:
                            to_add_vals = {
                                'amount':sum(request_advance_id.mapped("approved_amount")),
                                'input_type_id': rev_input_type_id.id,
                                'name': "Advance Salary"
                            }
                            each_emp.update({
                                'input_line_ids': [(0, 0, to_add_vals)]
                            })
                    else:
                        each_emp.input_line_ids = [(2, line.id) for line in each_emp.input_line_ids if line.input_type_id == rev_input_type_id]
        return res
    
    def action_payslip_done(self):
        res = super().action_payslip_done()
        for each in self:
            request_advance_id = self.env['request.advance'].search([('employee_id','=',each.employee_id.id),
                                                                    ('state','=','approved'),
                                                                    ('is_deduct_from_salary','=',False),
                                                                    ('approved_date','>=',each.date_from),
                                                                    ('approved_date','<=',each.date_to),
                                                                    ],limit=1)
            if request_advance_id:
                request_advance_id.is_deduct_from_salary = True
        return res