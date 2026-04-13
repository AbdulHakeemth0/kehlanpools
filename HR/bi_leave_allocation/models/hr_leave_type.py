from odoo import models, fields, api

class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    is_annual_leave =  fields.Boolean("Annual Leave",tracking=True)

    @api.model
    def _valid_field_parameter(self, field, name):
        if name == 'tracking' and field.type == 'boolean':
            return True
        return super(HrLeaveType, self)._valid_field_parameter(field, name)