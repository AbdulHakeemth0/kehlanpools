from odoo import models, fields, api, _
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    annual_leave_sal_apply = fields.Selection(selection = [
        ('yes','Yes'),
        ('no','No'),
    ],string = "Annual Leave Salary applicable")
    
    @api.depends('employee_id')        
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for rec in self:
            if rec.employee_id.is_gratuity_app:
                contract_ids = self.env['hr.contract'].sudo().search([
                    ('employee_id', '=', rec.employee_id.id),
                    ('state', '=', 'open')
                    ],limit=1)
                start_date = rec.employee_id.joining_date
                if contract_ids:
                    end_date = rec.employee_id.contract_ids.date_end
                    exp = relativedelta(end_date, start_date)
                    basic_salary = rec.contract_id.wage
                    if exp.years > 3 or (exp.years == 3 and exp.months > 0):
                        gratuity = (basic_salary)/12
                    else:
                        gratuity = (basic_salary/2)/12
                    existing_rule = rec.struct_id.rule_ids.filtered(lambda x: x.code == "EGPM")
                    if existing_rule:
                        rev_input_type_id = rec.env['hr.payslip.input.type'].search([('code', '=', "EGPM")], limit=1)
                        if not rev_input_type_id:
                            continue
                        existing_line = rec.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)
                        if existing_line:
                            existing_line.write({
                                'amount': gratuity,
                                'name': "Employee Gratuity Provision Monthly"
                            })
                        else:
                            to_add_vals = {
                                'amount':gratuity,
                                'input_type_id': rev_input_type_id.id,
                                'name': "Employee Gratuity Provision Monthly"
                            }
                            rec.update({
                                'input_line_ids': [(0, 0, to_add_vals)]
                            })
            else:
                rev_input_type_id = rec.env['hr.payslip.input.type'].search([('code', '=', "EGPM")], limit=1)
                if not rev_input_type_id:
                    continue
                existing_line = rec.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)
                if existing_line:
                    existing_line.unlink()
                            
            # annual leave salary
            leave_type = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)],limit=1)
            if leave_type:
                annual_leaves = self.env['hr.leave'].search([('employee_id','=', rec.employee_id.id),('holiday_status_id','=', leave_type.id),
                                                    ('state', '=', 'validate'),('request_date_from','>=',rec.date_from),('request_date_to','<=',rec.date_to)])
                existing_rule = rec.struct_id.rule_ids.filtered(lambda x: x.code == "ASL")
                rev_input_type_id = rec.env['hr.payslip.input.type'].search([('code', '=', "ASL")], limit=1)
                if existing_rule:
                    if annual_leaves:
                        existing_line = rec.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)
                        if existing_line:
                            existing_line.write({
                                'amount': annual_leaves.annual_leave_salary,
                                'name': "Annual Salary Leave"
                            })
                        else:
                            to_add_vals = {
                                'amount':annual_leaves.annual_leave_salary,
                                'input_type_id': rev_input_type_id.id,
                                'name': "Annual Salary Leave"
                            }
                            rec.update({
                                'input_line_ids': [(0, 0, to_add_vals)]
                            })
                    else:
                        rec.input_line_ids = [(2, line.id) for line in rec.input_line_ids if line.input_type_id == rev_input_type_id]
        return res
    

    # @api.model_create_multi
    # def create(self, vals_list):
    #     records = super(HrPayslip, self).create(vals_list)
    #     for res in records:
    #         if res.annual_leave_sal_apply == 'no':
    #             annual_leave_sal = res.input_line_ids.filtered(lambda x:x.code == 'ASL')
    #             if annual_leave_sal:
    #                 annual_leave_sal.unlink()
    #         if res.annual_leave_sal_apply == 'yes':
    #             annual_leave_sal = res.input_line_ids.filtered(lambda x:x.code == 'ASL')
    #             if not annual_leave_sal:
    #                 leave_type = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)])
    #                 if leave_type:
    #                     leave_type = leave_type[0]
    #                 leaves = self.env['hr.leave'].search([('employee_id','=', res.employee_id.id),('holiday_status_id','=', leave_type.id),
    #                                                           ('state', '=', 'validate'),('request_date_from','>=',res.date_from),('request_date_to','<=',res.date_to)])
    #                 if leaves:
    #                     existing_rule = res.struct_id.rule_ids.filtered(lambda x: x.code == "ASL")
    #                     if existing_rule:
    #                         rev_input_type_id = res.env['hr.payslip.input.type'].search([('code', '=', "ASL")], limit=1)
    #                         existing_line = res.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)
    #                         if existing_line:
    #                             existing_line.write({
    #                                 'amount': leaves.annual_leave_salary,
    #                                 'name': "Annual Salary Leave"
    #                             })
    #                         else:
    #                             to_add_vals = {
    #                                 'amount':leaves.annual_leave_salary,
    #                                 'input_type_id': rev_input_type_id.id,
    #                                 'name': "Annual Salary Leave"
    #                             }
    #                             res.update({
    #                                 'input_line_ids': [(0, 0, to_add_vals)]
    #                             })
    #     return records


    # def write(self, vals):
    #     result = super(HrPayslip,self).write(vals)
    #     for each in self:
    #         if each.annual_leave_sal_apply == 'no':
    #             annual_leave_sal = each.input_line_ids.filtered(lambda x:x.code == 'ASL')
    #             if annual_leave_sal:
    #                 annual_leave_sal.unlink()
    #         if each.annual_leave_sal_apply == 'yes':
    #             annual_leave_sal = each.input_line_ids.filtered(lambda x:x.code == 'ASL')
    #             if not annual_leave_sal:
    #                 leave_type = self.env['hr.leave.type'].search([('is_annual_leave', '=', True)])
    #                 if leave_type:
    #                     leave_type = leave_type[0]
    #                 leaves = self.env['hr.leave'].search([('employee_id','=', self.employee_id.id),('holiday_status_id','=', leave_type.id),
    #                                                           ('state', '=', 'validate'),('request_date_from','>=',each.date_from),('request_date_to','<=',each.date_to)])
    #                 if leaves:
    #                     existing_rule = each.struct_id.rule_ids.filtered(lambda x: x.code == "ASL")
    #                     if existing_rule:
    #                         rev_input_type_id = each.env['hr.payslip.input.type'].search([('code', '=', "ASL")], limit=1)
    #                         existing_line = each.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)
    #                         if existing_line:
    #                             existing_line.write({
    #                                 'amount': leaves.annual_leave_salary,
    #                                 'name': "Annual Salary Leave"
    #                             })
    #                         else:
    #                             to_add_vals = {
    #                                 'amount':leaves.annual_leave_salary,
    #                                 'input_type_id': rev_input_type_id.id,
    #                                 'name': "Annual Salary Leave"
    #                             }
    #                             each.update({
    #                                 'input_line_ids': [(0, 0, to_add_vals)]
    #                             })
    #     return result


   