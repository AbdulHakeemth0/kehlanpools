from odoo import models, fields, api
from odoo.exceptions import UserError


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'


    approver_id = fields.Many2one('res.users', string='Approver')
    reject_reason = fields.Text(string='Refuse Reason')

    @api.model_create_multi
    def create(self, vals_list):
        records = super(HrAttendance, self).create(vals_list)
        for res in records:
            # if res.approver_id:
            #     res.overtime_status = "to_approve"
                res.send_approval_notification()
        return records

    def send_approval_notification(self):
        approver_id = self.env['hr.employee'].sudo().search([('job_id.attendance_approver', '=' , True)])
        for approver in approver_id:
            if approver.user_id:
                data = {
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'hr.attendance')], limit=1).id,
                    'user_id': approver.user_id.id,
                    'activity_type_id': self.env.ref('bi_time_approval.mail_activity_data_approve_reject').id,
                    'summary': 'Attendance Approval Required',
                    'note': 'Please review and approve the attendance for %s.' % (self.employee_id.name),
                }
                self.env['mail.activity'].sudo().create(data)

    def action_approve_overtime(self):
        if not self.env.user.employee_id.job_id.attendance_approver:
            raise UserError("You don't have the permissions to approve the attendance.Please contact the 'Attendance Approver'...!")
        res = super(HrAttendance, self).action_approve_overtime()
        self.send_team_lead_notification()
        return res

    def action_refuse_overtime(self):
        for each in self:
            user_job = each.env.user.employee_id.job_id
            if not each.reject_reason:
                raise UserError("Please provide a rejection reason before refusing the overtime.")
            if not user_job.attendance_approver:
                raise UserError("You do not have the required permissions to refuse overtime.")
            res = super(HrAttendance, self).action_refuse_overtime()
            each.send_team_lead_notification()
            return res

    def send_team_lead_notification(self):
        for each in self:
            team_leads = each.env['hr.employee'].sudo().search([('is_team_lead', '=', True)])
            activity_type_id = each.env.ref('bi_time_approval.mail_activity_data_approve_reject').id
            summary = 'Attendance %s Notification' % ('Approved' if each.overtime_status == 'approved' else 'Rejected')
            note = 'The attendance for %s has been %s.' % (each.employee_id.name, each.overtime_status)
            for team_lead in team_leads:
                data = {
                    'res_id': each.id,
                    'res_model_id': each.env['ir.model'].sudo().search([('model', '=', 'hr.attendance')], limit=1).id,
                    'user_id': team_lead.user_id.id,
                    'activity_type_id': activity_type_id,
                    'summary': summary,
                    'note': note,
                }
                each.env['mail.activity'].sudo().create(data)