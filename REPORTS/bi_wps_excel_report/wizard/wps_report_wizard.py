from odoo import fields, models
from datetime import date


class WPSSalaryWizard(models.TransientModel):
    _name = 'wizard.wps.salary'
    _description = 'WPS Salary Excel Report'

    data_month = fields.Selection(
        [("1", "January"),
         ("2", "February"),
         ("3", "March"),
         ("4", "April"),
         ("5", "May"),
         ("6", "June"),
         ("7", "July"),
         ("8", "August"),
         ("9", "September"),
         ("10", "October"),
         ("11", "November"),
         ("12", "December"),], string="Month", required=True, default=str(date.today().month))
    data_year = fields.Selection(selection='get_years_selection', string='Year', default=str(date.today().year),
                                 required=True)
    
    def get_years_selection(self):
        year_list = []
        for i in range(2022, 5036):
            year_list.append((str(i), str(i)))
        return year_list

    def print_excel(self):
        data={
            'ids' : self.ids,
            'models' : self._name,
            'form'   : {'from_date': self.data_month,
                        'to_date'  : self.data_year,
                    }
            }
        return self.env.ref("bi_wps_excel_report.action_view_report_wps_salary_xlsx").report_action(self,data=data)