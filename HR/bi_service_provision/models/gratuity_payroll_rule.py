from odoo import models, fields, api, _
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta


class HrPayslip(models.Model):
    _inherit = "hr.payslip"
    
    # gratuity payout 
    @api.depends('employee_id','contract_id', 'struct_id', 'date_from', 'date_to')        
    def _compute_input_line_ids(self):
        res = super()._compute_input_line_ids()
        for employee in self:
            rev_input_type_id = employee.env['hr.payslip.input.type'].search([('code', '=', "GEOS")], limit=1)
            if not rev_input_type_id:
                continue
            existing_line = employee.input_line_ids.filtered(lambda line: line.input_type_id == rev_input_type_id)
            if not employee.employee_id.active:
                total_gratuity = sum(self.env['gratuity.provision'].search([('employee_id', '=', employee.employee_id.id)]).mapped('gratuity_provision_line_ids.amount'))
                existing_rule = employee.struct_id.rule_ids.filtered(lambda x: x.code == "GEOS")
                if existing_rule:
                    if total_gratuity > 0:
                        if existing_line:
                            existing_line.write({
                                'amount': total_gratuity,
                                'name': "Gratuity End of Service Payout"
                            })
                        else:
                            to_add_vals = {
                                'amount': total_gratuity,
                                'input_type_id': rev_input_type_id.id,
                                'name': "Gratuity End of Service Payout"
                            }
                            employee.update({'input_line_ids': [(0, 0, to_add_vals)]})
                    else:
                        if existing_line:
                            existing_line.unlink()
            else:
                if existing_line:
                    existing_line.unlink()
        return res
