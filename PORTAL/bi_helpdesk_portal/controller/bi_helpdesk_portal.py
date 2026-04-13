# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import UserError

class CustomHelpdeskPortal(CustomerPortal):


    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'ticket_count' in counters:
            if request.env['res.users'].browse(request.uid).employee_id or request.env['res.users'].browse(request.uid).partner_id:
                if request.env['res.users'].browse(request.uid).employee_id or request.env['res.users'].browse(request.uid).partner_id.customer_rank == 1:
                    values['ticket_count'] =  request.env['helpdesk.ticket'].search_count(self._prepare_helpdesk_tickets_domain()) \
                        if request.env['helpdesk.ticket'].has_access('read') else 0
                    if not  request.env['helpdesk.ticket'].search_count(self._prepare_helpdesk_tickets_domain()):
                        values['ticket_count'] = 1
        return values

    @http.route(['/my/tickets/new'], type='http', auth="user", website=True)
    def create_form(self, **kw):
        helpdesk_teams = request.env['helpdesk.team'].sudo().search([('company_id','=',request.env.company.id)])
        # assigned_to = request.env['res.users'].sudo().search([])
        # customer_id = request.env['res.partner'].sudo().search([])
        return request.render("bi_helpdesk_portal.portal_ticket_create", {
            'page_name': 'helpdesk_ticket',
            'helpdesk_teams': helpdesk_teams,
            # 'assigned_to': assigned_to,
            # 'customer_id': customer_id,
            'error': kw.get('error'),
        })


    @http.route(['/my/tickets/create_new_ticket'], type='http', auth="user", methods=['POST'], website=True, csrf=True)
    def create_new_ticket(self, **post):
        """Handle ticket creation form submission."""
        try:
            ticket_name = post.get('ticket_name', '').strip()
            ticket_type = post.get('ticket_type', '').strip()
            description = post.get('description', '').strip()
            phone_id = post.get('phone_id', '').strip()
            email_id = post.get('email_id', '').strip()
            remark = post.get('remark', '').strip()
            helpdesk_team_id = int(post.get('helpdesk_teams', 0)) if post.get('helpdesk_teams') else False
            # assigned_to_id = int(post.get('assigned_to', 0)) if post.get('assigned_to') else False
            customer_id = request.env['res.users'].browse(request.uid).partner_id.id

            if not ticket_name or not description:
                return request.redirect('/my/tickets/new') 

            request.env['helpdesk.ticket'].sudo().create({
                'name': ticket_name,
                'ticket_type': ticket_type,
                'description': description,
                'partner_phone': phone_id,
                'email_cc': email_id,
                'remarks':remark,
                'team_id': helpdesk_team_id,
                # 'user_id': assigned_to_id,
                'partner_id': customer_id,
            })

            return request.redirect(f"/my/tickets")
        except UserError as e:
            return request.redirect('/my/tickets/create?error=%s' % str(e))
        except Exception as e:
            return request.redirect('/my/tickets/create?error=%s' % str(e))
        

    # @http.route('/my/tickets/view_ticket_info', type='http', auth="user", website=True)
    # def view_ticket_info(self, **kwargs):
    #     ticket_id = kwargs.get('ticket_id')
    #     if ticket_id:
    #         ticket = request.env['helpdesk.ticket'].sudo().browse(int(ticket_id))
    #         if ticket.exists():
    #             ticket.sudo().write({
    #                 'name': kwargs.get('ticket_name'),
    #                 'team_id': int(kwargs.get('helpdesk_teams')) if kwargs.get('helpdesk_teams') else False,
    #                 'ticket_type': kwargs.get('ticket_type'),
    #                 'description': kwargs.get('description'),

    #             })
    #     else:
    #         request.env['helpdesk.ticket'].sudo().create({
    #             'name': kwargs.get('ticket_name'),
    #             'team_id': int(kwargs.get('helpdesk_teams')) if kwargs.get('helpdesk_teams') else False,
    #             'ticket_type': kwargs.get('ticket_type'),
    #             'description': kwargs.get('description'),
            
    #         })
    #     return request.redirect('/AllTickets')
    

    @http.route(['/my/tickets/state_hold'], type='http', auth="user", website=True, csrf=False)
    def ticket_state_changed_hold(self, **post):
        hold_state = request.env['helpdesk.stage'].sudo().search([('is_hold','=',True)])
        ticket = request.env['helpdesk.ticket'].browse(int(post.get('ticket_id')))
        if ticket:
            ticket.stage_id = hold_state.id
        return request.redirect("/my/tickets")

    @http.route(['/my/tickets/state_solved'], type='http', auth="user", website=True, csrf=False)
    def ticket_state_changed_solved(self, **post):
        solved_state = request.env['helpdesk.stage'].sudo().search([('is_solved','=',True)])
        ticket = request.env['helpdesk.ticket'].browse(int(post.get('ticket_id')))
        if ticket:
            ticket.stage_id = solved_state.id
        return request.redirect(f"/my/tickets")
        
    @http.route(['/my/tickets/state_cancel'], type='http', auth="user", website=True, csrf=False)
    def ticket_state_changed_cancelled(self, **post):
        cancel_state = request.env['helpdesk.stage'].sudo().search([('is_cancel','=',True)])
        ticket = request.env['helpdesk.ticket'].browse(int(post.get('ticket_id')))
        if ticket:
            ticket.stage_id = cancel_state.id
        return request.redirect(f"/my/tickets")


    @http.route(['/AllTickets', '/AllTickets/page/<int:page>'], type='http', auth="user", website=True)
    def helpdesk_tickets_portal(self, search=None, search_in='All'):
        """Display the tickets raised in the portal."""
        partner_id = request.env['res.partner'].browse(request.uid)
        helpdesk_tickets = request.env['helpdesk.ticket'].sudo().search([
            ('partner_id', '=', partner_id.id)
        ],)

        return request.render('bi_helpdesk_portal.portal_ticket_create', {
            'all_tickets': helpdesk_tickets,
            'page_name': 'all_tickets',
        })


