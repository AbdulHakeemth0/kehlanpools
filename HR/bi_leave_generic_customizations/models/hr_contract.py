from odoo import models, fields, _
from datetime import date, datetime,timedelta
from dateutil.relativedelta import relativedelta



class hrContract(models.Model):
    _inherit = "hr.contract"


    def update_employee_contract(self):
        current_date = date.today()
        cutoff_date = current_date + timedelta(days=45)
        new_contracts = self.env['hr.contract'].sudo().search([
            ('state', '=', 'draft'),
            ('date_start', '<=', current_date)
        ])
        running_contracts = self.env['hr.contract'].sudo().search([
            ('state', '=', 'open'),
            ('date_end', '<=', current_date) 
        ])
        expiring_contracts = self.env['hr.contract'].sudo().search([
                                    ('state', '=', 'open'),
                                    ('date_end', '>=', current_date),
                                    ('date_end', '<=', cutoff_date),
                                ])
        for contract in expiring_contracts:
            users = self.env.ref("bi_leave_generic_customizations.group_hr_related").users
            model = self.env["ir.model"].sudo().search([("model", "=", "hr.contract")],limit=1)   
            for user in users:
                data = {
                    "res_id": contract.id,
                    "res_model_id": model.id,
                    "user_id": user.id,
                    "summary" : f"Contract for {contract.employee_id.name} is expiring on {contract.date_end}",
                    "activity_type_id": self.env.ref("bi_leave_generic_customizations.contract_expired_activity_id").id
                }
            self.env["mail.activity"].sudo().create(data)
        if new_contracts:
            new_contracts.write({'state': 'open'})
        if running_contracts:
            running_contracts.write({'state': 'close'})
             
    