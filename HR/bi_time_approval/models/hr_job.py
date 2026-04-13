from odoo import models, fields

class HrJob(models.Model):
    _inherit = 'hr.job'

    attendance_approver = fields.Boolean(string="Attendance Approver", help="Set this if employees in this position can approve attendance.")
    is_teamlead = fields.Boolean(string="Is Team Lead", help="Set this if employees in this position are team leaders.")
    is_staff = fields.Boolean(
        string='Staff',
    )
    is_technician = fields.Boolean(
        string='Technician',
    )
    is_timeoff_approver = fields.Boolean(
        string='Time Off Approver',
    )
    is_coo = fields.Boolean(
        string='Is COO',
    )

    is_ceo = fields.Boolean(
        string='Is CEO',
    )