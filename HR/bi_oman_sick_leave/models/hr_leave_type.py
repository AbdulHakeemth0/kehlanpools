from odoo import models, fields


class HrLeave(models.Model):
    _inherit = 'hr.leave.type'

    is_sick_leave_oman = fields.Boolean("Oman Sick Leave")