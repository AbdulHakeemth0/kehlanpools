from odoo import models, fields, api, _
from odoo.exceptions import UserError
class HrLeave(models.Model):
    _inherit = 'hr.leave'

    is_notify = fields.Boolean(string="Is Notify")            

    def action_notify(self):
        for leave in self:
            if not leave.employee_id.leave_manager_id:
                raise UserError(_("No Leave Manager assigned for this employee."))
            model = self.env["ir.model"].sudo().search([("model", "=", "hr.leave")],limit=1)
            manager = leave.employee_id.leave_manager_id
            if manager:
                data = {
                    "res_id": leave.id,
                    "res_model_id": model.id,
                    "user_id": manager.id,
                    "summary": f'{leave.employee_id.name} Time off has been created {self.env.user.name}',
                    "activity_type_id": self.env.ref("bi_time_approval.time_off_notify_activity_id").id
                }
                self.env["mail.activity"].sudo().create(data)
            leave.is_notify = True

    