from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')
    def _compute_input_line_ids(self):
        """ Computes Overtime and updates payslip inputs without duplication or leftover entries """
        res = super()._compute_input_line_ids()
        for payslip in self:
            if payslip.employee_id and payslip.struct_id:
            # if not payslip.employee_id or not payslip.date_from or not payslip.date_to:
            #     payslip.input_line_ids = [(5, 0, 0)]  # Clear all inputs if data is missing
            #     continue

                # Fetch existing OT input lines
                existing_normal_ot = payslip.input_line_ids.filtered(lambda i: i.code == 'NORMAL_OT')
                existing_holiday_ot = payslip.input_line_ids.filtered(lambda i: i.code == 'HOLIDAY_OT')

                # Fetch Overtime Records in the Payslip Period
                overtime_records = self.env['bi.overtime'].search([
                    ('employee_id', '=', payslip.employee_id.id),
                    ('first_check_in', '>=', payslip.date_from),
                    ('last_check_out', '<=', payslip.date_to)
                ])
                if overtime_records:
                    normal_ot_total = sum(overtime_records.filtered(lambda o: o.overtime_type == 'normal_ot').mapped('overtime_pay'))
                    holiday_ot_total = sum(overtime_records.filtered(lambda o: o.overtime_type == 'holiday_ot').mapped('overtime_pay'))

                    # Ensure Overtime Input Types Exist
                    input_type_normal_ot = self.env.ref('bi_overtime_request.input_type_normal_ot', raise_if_not_found=False)
                    input_type_holiday_ot = self.env.ref('bi_overtime_request.input_type_holiday_ot', raise_if_not_found=False)

                    input_line_vals = []

                    # Handle Normal Overtime
                    if normal_ot_total > 0 and input_type_normal_ot:
                        if existing_normal_ot:
                            existing_normal_ot.amount = normal_ot_total
                        else:
                            input_line_vals.append((0, 0, {
                                'input_type_id': input_type_normal_ot.id,
                                'code': 'NORMAL_OT',
                                'amount': normal_ot_total,
                                'name': 'Normal OT',
                            }))
                    elif existing_normal_ot:
                        existing_normal_ot.unlink()  # Remove old OT input when OT is 0

                    # Handle Holiday Overtime
                    if holiday_ot_total > 0 and input_type_holiday_ot:
                        if existing_holiday_ot:
                            existing_holiday_ot.amount = holiday_ot_total
                        else:
                            input_line_vals.append((0, 0, {
                                'input_type_id': input_type_holiday_ot.id,
                                'code': 'HOLIDAY_OT',
                                'amount': holiday_ot_total,
                                'name': 'Holiday OT',
                            }))
                    elif existing_holiday_ot:
                        existing_holiday_ot.unlink()  # Remove old OT input when OT is 0

                    # Append new inputs to existing ones
                    if input_line_vals:
                        payslip.update({'input_line_ids': input_line_vals})

        return res
