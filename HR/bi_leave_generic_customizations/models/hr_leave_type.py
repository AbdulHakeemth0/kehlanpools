from odoo import models, fields


class HrLeave(models.Model):
    _inherit = 'hr.leave.type'

    is_maternity_leave = fields.Boolean("Maternity Leave")
    is_paternity_leave = fields.Boolean("Paternity Leave")
    is_marriage_leave = fields.Boolean("Marriage Leave")
