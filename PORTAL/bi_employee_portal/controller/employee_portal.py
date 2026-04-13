from odoo.http import request, Controller, route
from odoo import http,fields
# from odoo.exceptions import ValidationError

from odoo.addons.portal.controllers import portal # type: ignore


class EmployeePortal(portal.CustomerPortal):
    """To get the timeoff and allocations in the employee portal"""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        # time off
        if 'employee_portal' in counters:
            if request.env['res.users'].browse(request.uid).employee_id:
                if request.env['res.users'].browse(request.uid).employee_id.is_team_lead:
                    values['employee_portal'] = request.env['hr.leave'].search_count([]) \
                        if request.env['hr.leave'].check_access_rights('read', raise_exception=False) else 0
                    if not request.env['hr.leave'].search_count([]):
                        values['employee_portal'] = 1
        return values

    # request time off
    @http.route(['/request_timeoff'], type='http', auth="user", website=True)
    def request_for_timeoff(self, **kw):
        employee = request.env['res.users'].browse(request.uid).employee_id
        today_date = fields.Date.today()
        leave_types = request.env['hr.leave.type'].search([])
        data =leave_types.get_allocation_data(employee, today_date)[employee]
        paid_timeoff_virtual_remaining_leaves = 0
        sick_timeoff_virtual_remaining_leaves = 0
        for i, leave in enumerate(data):
            if leave[0] == 'Annual Leave':
                paid_timeoff_virtual_remaining_leaves = float(leave[1]['virtual_remaining_leaves'])
            elif leave[0] == 'Sick Time Off':
                sick_timeoff_virtual_remaining_leaves = float(leave[1]['virtual_remaining_leaves'])
        paid_timeoff = paid_timeoff_virtual_remaining_leaves
        sick_timeoff = sick_timeoff_virtual_remaining_leaves

        domain = ['|',
            ('company_id', 'in', [request.env.company.id, False]),
            # ('requires_allocation', '=', 'no'),
            ('has_valid_allocation', '=', True),
        ]
        timeoff_type_list = request.env['hr.leave.type'].search(domain)
        team_id = request.env['hr.employee.team'].sudo().search([('team_lead_id.user_id', '=', request.uid)])
        if team_id:
            team_mem = team_id.members_ids
        else:
            domain1 = [
                    ('parent_id', '=', employee.id)
            ]
            team_mem = request.env['hr.employee'].sudo().search(domain1)

        return request.render('bi_employee_portal.portal_request_new_timeoff_views', {
            'page_name': 'common_timeoff',
            'team_members': team_mem,
            'timeoff_types': timeoff_type_list,
            'sick_time_off_days': sick_timeoff,
            'paid_time_off_days': paid_timeoff,
        })

    # create new time off
    @http.route(['/my/new_timeoff'], type='http', auth="public", website=True)
    def create_new_timeoff(self, **post):
        employee = request.env['res.users'].browse(request.uid).employee_id
        employee_id = request.env['hr.employee'].sudo().search([('id','=',int(post.get('employee_id')))]).id
        new_timeoff = request.env['hr.leave'].sudo().create({
            'employee_id': employee_id,
            'holiday_status_id': int(post.get('holiday_status_id')),
            'request_date_from': post.get('date_from'),
            'request_date_to': post.get('date_to'),
            'duration_display': post.get('duration'),
            'name': post.get('description'),
        })
        vals = {
            'new_timeoff': new_timeoff
        }
        return request.redirect(f"/Commontimeoff")

    # Time off
    @http.route(['/Commontimeoff', '/Commontimeoff/page/<int:page>'], type='http', auth="user", website=True)
    def employee_portal(self, search=None, search_in='All'):
        """To search the timeoff data in the portal"""
        employee = request.env['res.users'].browse(request.uid).employee_id
        leave_id = request.env['hr.leave'].sudo().search([
            ('employee_id', '=', employee.id)
        ])
        today_date = fields.Date.today()
        leave_types = request.env['hr.leave.type'].search([])
        data =leave_types.get_allocation_data(employee, today_date)[employee]
        paid_timeoff_virtual_remaining_leaves = 0
        sick_timeoff_virtual_remaining_leaves = 0
        for i, leave in enumerate(data):
            if leave[0] == 'Annual Leave':
                paid_timeoff_virtual_remaining_leaves = float(leave[1]['virtual_remaining_leaves'])
            elif leave[0] == 'Sick Time Off':
                sick_timeoff_virtual_remaining_leaves = float(leave[1]['virtual_remaining_leaves'])
        paid_timeoff = paid_timeoff_virtual_remaining_leaves
        sick_timeoff = sick_timeoff_virtual_remaining_leaves
        searchbar_inputs = {
            'All': {'label': 'All', 'input': 'All', 'domain': [('create_uid', '=', request.env['res.users'].browse(request.uid).id)]},
        }
        search_domain = searchbar_inputs[search_in]['domain']
        search_timeoff = leave_id.search(search_domain)
        return request.render('bi_employee_portal.portal_my_home_timeoff_views',
                              {
                                  'common_timeoff': search_timeoff,
                                  'page_name': 'common_timeoff',
                                #   'search': search,
                                  'paid_timeoff': paid_timeoff,
                                  'sick_timeoff': sick_timeoff,
                                #   'search_in': search_in,
                                #   'searchbar_inputs': searchbar_inputs
                              })
