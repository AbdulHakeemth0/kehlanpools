from odoo import models, fields, api

class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    team_member_ids = fields.Many2many('hr.employee', string="Team Members")






