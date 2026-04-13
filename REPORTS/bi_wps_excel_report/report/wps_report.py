from odoo import models, fields, api
from datetime import datetime
import calendar


class ReportExcel(models.AbstractModel):
    _name = "report.bi_wps_excel_report.wps_order_report_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "WPS Excel Report"

    def generate_xlsx_report(self, workbook, data, lines):
        # Get the selected month and year from the data passed to the report
        month = data['form']['from_date']
        year = data['form']['to_date']

        # Get the last day of the selected month
        last_day_of_month = calendar.monthrange(int(year), int(month))[1]

        # Get the range for the selected month (as datetime.date objects)
        date_from = datetime.strptime(f'{year}-{month}-01', '%Y-%m-%d').date()
        date_to = datetime.strptime(f'{year}-{month}-{last_day_of_month}', '%Y-%m-%d').date()

        # Search for employees who have an active contract and a payslip within the selected month
        employees = self.env['hr.employee'].sudo().search([
            ('contract_id', '!=', False),  # Employee should have an active contract
        ])

        # Filter employees who have an active contract during the selected period and have a payslip
        valid_employees = []
        for employee in employees:
            contract = employee.contract_id
            # Check if the contract is active (current date should be within contract dates)
            if contract and contract.date_start <= date_to and (
                    not contract.date_end or contract.date_end >= date_from):
                # Check if the employee has a payslip in the selected month
                payslip = self.env['hr.payslip'].search([
                    ('employee_id', '=', employee.id),
                    ('date_from', '>=', date_from),
                    ('date_to', '<=', date_to)
                ], limit=1)

                if payslip:
                    valid_employees.append(employee)

        # Prepare to generate the XLSX report
        ws = workbook.add_worksheet('Employee Salary Information')

        # Set up column widths and formats
        ws.set_column('A:A', 15)
        ws.set_column('B:B', 15)
        ws.set_column('C:C', 15)
        ws.set_column('D:D', 15)
        ws.set_column('E:E', 15)
        ws.set_column('F:F', 15)
        ws.set_column('G:G', 15)
        ws.set_column('H:H', 15)
        ws.set_column('I:I', 15)
        ws.set_column('J:J', 15)
        ws.set_column('K:K', 15)
        ws.set_column('L:L', 15)
        ws.set_column('M:M', 15)
        ws.set_column('N:N', 15)
        ws.set_column('O:O', 15)

        # Formatting
        title_format = workbook.add_format({'bold': True, 'font_size': 14, 'align': 'center'})
        heading_format = workbook.add_format(
            {'bold': True, 'font_size': 10, 'border': True, 'align': 'center', 'valign': 'vcenter'})
        text_format = workbook.add_format({'font_size': 10, 'border': True, 'align': 'left'})
        digit_format = workbook.add_format({'font_size': 10, 'border': True, 'align': 'right'})

        # Merge title cells
        ws.merge_range('A1:O2', 'Employee Salary Information', title_format)

        # Header columns
        headers = ['Reference Number', 'Employee ID Type', 'Employee ID', 'Employee Name', 'Employee BIC Code',
                   'Employee Account', 'Salary Frequency', 'Number of Working Days', 'Net Salary', 'Basic Salary',
                   'Extra Hours', 'Extra Income', 'Deductions', 'Social Security Deductions', 'Notes/Comments']

        # Write headers
        row = 2
        col = 0
        for header in headers:
            ws.merge_range(row, col, row + 1, col, header, heading_format)
            col += 1

        # Populate employee data
        row += 2
        serial_no = 1
        for employee in valid_employees:
            # Fetch payslip information
            payslip = self.env['hr.payslip'].search([
                ('employee_id', '=', employee.id),
                ('date_from', '>=', date_from),
                ('date_to', '<=', date_to)
            ], limit=1)

            if payslip:
                contract = employee.contract_id
                salary_frequency = contract.schedule_pay if contract else ''
                basic_salary = contract.wage
                extra_hours = 0.0
                extra_income = 0.0
                hourly_rate = 0.0
                for worked_day in payslip.worked_days_line_ids:
                    if worked_day.work_entry_type_id.code == 'OVERTIME':
                        extra_hours += worked_day.number_of_hours
                        hourly_rate = basic_salary / 160 if basic_salary else 0
                extra_income = extra_hours * hourly_rate
                total_deductions = sum(
                    payslip.line_ids.filtered(lambda line: line.code == 'DEDUCTION').mapped('total'))
                net_salary = basic_salary + extra_income
                total_net = net_salary - total_deductions
                days_in_month = calendar.monthrange(int(year), int(month))[1]
                comments = payslip.note

                ws.write(row, 0, serial_no, text_format)  # Reference Number
                ws.write(row, 1, employee.employee_id_type or '', text_format)  # Employee ID Type
                ws.write(row, 2, employee.barcode or '', text_format)  # Employee ID
                ws.write(row, 3, employee.name, text_format)  # Employee Name
                ws.write(row, 4, employee.bank_account_id.acc_number or '', text_format)  # BIC Code
                ws.write(row, 5, employee.bank_account_id.bank_id.name or '', text_format)  # Bank Account
                ws.write(row, 6, salary_frequency, text_format)  # Salary Frequency
                ws.write(row, 7, days_in_month, digit_format)  # Number of Working Days
                ws.write(row, 8, total_net, digit_format)  # Net Salary (Basic Salary)
                ws.write(row, 9, basic_salary, digit_format)  # Basic Salary (simplified for now)
                ws.write(row, 10, extra_hours, digit_format)  # Extra Hours (example)
                ws.write(row, 11, extra_income, digit_format)  # Extra Income (example)
                ws.write(row, 12, total_deductions, digit_format)  # Deductions (example)
                ws.write(row, 13, 0.0, digit_format)  # Social Security Deductions (example)
                ws.write(row, 14, comments, text_format)  # Notes/Comments

                serial_no += 1
                row += 1
