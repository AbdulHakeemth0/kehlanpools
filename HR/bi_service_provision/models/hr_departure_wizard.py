from odoo import models, fields 


class HrDepartureWizard(models.TransientModel):
    _inherit = "hr.departure.wizard"
    
    def action_register_departure(self):
        res = super(HrDepartureWizard,self).action_register_departure()
        for rec in self:
            if rec.employee_id.contract_ids:
                for contract in rec.employee_id.contract_ids:
                    if contract.active and contract.date_end == False:
                       contract.date_end =  rec.departure_date
                    else:
                       contract.date_end    
        return res