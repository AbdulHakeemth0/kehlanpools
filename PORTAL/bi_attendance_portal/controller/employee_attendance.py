from odoo.http import request, Controller, route
from odoo.addons.portal.controllers import portal
from datetime import datetime, timedelta
from odoo import api, models, fields

class EmployeeAttendancePortal(portal.CustomerPortal):
    """Portal controller for managing employee check-in and check-out."""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'employee_attendance_portal' in counters:
            if request.env['res.users'].browse(request.uid).employee_id:
                if request.env['res.users'].browse(request.uid).employee_id.is_team_lead:
                    values['employee_attendance_portal'] = request.env['hr.attendance'].search_count([]) \
                        if request.env['hr.attendance'].check_access_rights('read', raise_exception=False) else 0
                    if not request.env['hr.attendance'].search_count([]):
                        values['employee_attendance_portal'] = 1
        return values

    # def _get_team_members(self):
    #     """Fetch team members of the logged-in user's team."""
    #     employee = request.env['res.users'].browse(request.uid).employee_id
    #     team = request.env['hr.employee.team'].sudo().search([('team_lead_id', '=', employee.id)], limit=1)
    #     if team:
    #         team_members = [member for member in team.members_ids if member.id != employee.id]
    #         return team_members
    #     else:
    #         return request.env['hr.employee']

    def _get_team_members(self):
        """Fetch team members of the logged-in user's team."""
        employee = request.env['res.users'].browse(request.uid).employee_id
        team = request.env['hr.employee.team'].sudo().search([('team_lead_id', '=', employee.id)], limit=1) 
        return team.members_ids if team else request.env['hr.employee'].sudo().search([])

    @route(['/check_in_form'], type='http', auth="user", website=True)
    def check_in_form(self, **post):
        """Render the manual check-in form with team members selection."""
        team_members = self._get_team_members()
        return request.render('bi_attendance_portal.check_in_form', {
            'team_members': team_members,
        })
    
    @route(['/submit_check_in'], type='http', auth="user", methods=['POST'], website=True)
    def submit_check_in(self, **post):
        """Handle the manual check-in form submission for the logged-in user and selected team members."""
        employee = request.env['res.users'].browse(request.uid).employee_id  
        check_in_time = post.get('check_in_time')
        # selected_member_ids = request.httprequest.form.getlist('selected_members', [])  
        selected_member_ids = request.httprequest.form.getlist('selected_members')  
        
        try:
            check_in_time = check_in_time.replace('T', ' ')
            check_in_time_dt = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return request.redirect('/Commonattendance?error=invalid_datetime')

        valid_member_ids = [int(member_id) for member_id in selected_member_ids if member_id.strip()]
        # valid_member_ids.append(employee.id)  
        valid_member_ids = list(set(valid_member_ids))         
        
        check_in = check_in_time_dt - timedelta(hours=5,minutes=30)
        check_in_time = check_in.strftime("%Y-%m-%d %H:%M:%S")

        for member_id in valid_member_ids: 
            attendence = request.env['hr.attendance'].sudo().create({
                'employee_id': member_id,
                'check_in': check_in_time,
            })

        return request.redirect('/Commonattendance')

    @route(['/check_out_form'], type='http', auth="user", website=True)
    def check_out_form(self, **post):
        """Render the manual check-out form."""
        team_members = self._get_team_members()
        return request.render('bi_attendance_portal.check_out_form', {
            'team_members': team_members,
        })

    @route('/submit_check_out', type='http', auth="user", methods=['POST'], website=True)
    def submit_check_out(self, **post):
        employee = request.env['res.users'].browse(request.uid).employee_id
        # employee_team = request.env['hr.employee.team'].sudo().search([('team_lead_id', '=', employee.id)], limit=1)
        # selected_members = []

        # if employee_team:
        #     selected_members = request.env['hr.employee'].browse(post.get('selected_members', '').split(','))
        #     selected_members |= employee

        # else:
        #     selected_members = [employee]

        # for member in selected_members:
        #     attendance = request.env['hr.attendance'].sudo().search([
        #         ('employee_id', '=', member.id),
        #         ('check_out', '=', False)
        #     ], limit=1)
        selected_member_ids = request.httprequest.form.getlist('selected_members')  

        valid_member_ids = [int(member_id) for member_id in selected_member_ids if member_id.strip()]
        # valid_member_ids.append(employee.id)  
        valid_member_ids = list(set(valid_member_ids))
        check_out_time = post.get('check_out_time')  

        try:
            check_out_time = check_out_time.replace('T', ' ')
            check_out_time = datetime.strptime(check_out_time, "%Y-%m-%d %H:%M")
        except ValueError:
            return request.redirect('/Commonattendance?error=invalid_datetime')
        check_out = check_out_time - timedelta(hours=5,minutes=30)
        check_out_time = check_out.strftime("%Y-%m-%d %H:%M:%S")
        for member_id in valid_member_ids:
            attendance = request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', member_id),
                ('check_out', '=', False)
            ], limit=1)

            if attendance:
                attendance.write({
                    'check_out': check_out_time,
                })

        return request.redirect('/Commonattendance')

    @route(['/Commonattendance', '/Commonattendance/page/<int:page>'], type='http', auth="user", website=True)
    def employee_attendance_portal(self, search=None, search_in='All', **kwargs):
        """Display the attendance records for the employee in the portal."""
        employee = request.env['res.users'].browse(request.uid).employee_id
        employee_team = request.env['hr.employee.team'].sudo().search([('team_lead_id', '=', employee.id)], limit=1)
        if employee_team:
            all_member_ids = [employee.id] + [member.id for member in employee_team.members_ids]
        else:
            all_member_ids = [employee.id]

        attendance_ids = request.env['hr.attendance'].sudo().search([
            ('employee_id', 'in', all_member_ids)
        ], order="check_in desc")

        last_attendance = attendance_ids and attendance_ids[0] or None
        # team = request.env['hr.employee.team'].sudo().search([('team_lead_id', '=', employee.id)], limit=1)

        return request.render('bi_attendance_portal.portal_my_home_attendance_views', {
            'common_attendance': attendance_ids,
            'page_name': 'common_attendance',
            'last_attendance': last_attendance,
            'team': employee.is_team_lead,
        })
