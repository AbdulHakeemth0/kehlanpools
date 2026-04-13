from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal

class AMCPortalController(portal.CustomerPortal):
    """To display AMC Plans in the portal"""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'amc_plan_portal' in counters:
            values['amc_plan_portal'] = request.env['amc.plan'].search_count([]) \
                if request.env['amc.plan'].check_access_rights('read', raise_exception=False) else 0
            if not request.env['amc.plan'].search_count([]):
                values['amc_plan_portal'] = 1
        return values

    @http.route(['/amc_overview'], type='http', auth="user", website=True)
    def amc_overview(self, **post):
        """AMC Plans Overview Page."""
        # Fetch all AMC Plans against the customer
        amc_plans = request.env['amc.plan'].search([('customer_id', '=', request.env.user.partner_id.id)])

        return request.render('bi_amc_portal.amc_plans_overview_template', {
            'amc_plans': amc_plans,
            'page_name': 'amc_overview',
        })

    @http.route(['/amc_contract/<int:amc_id>'], type='http', auth="user", website=True)
    def amc_contract(self, amc_id, **post):
        """AMC Contract Form Page (readonly) for a specific AMC plan."""
        amc_plan = request.env['amc.plan'].browse(amc_id)
        
        if amc_plan.customer_id.id != request.env.user.partner_id.id:
            return request.redirect('/amc_overview')

        return request.render('bi_amc_portal.amc_plan_contract_template', {
            'amc_plan': amc_plan,
            'page_name': 'amc_contract',
        })

    @http.route(['/amc_history/<int:amc_id>'], type='http', auth="user", website=True)
    def amc_history(self, amc_id, **post):
        """AMC History Page for a specific plan."""
        amc_plan = request.env['amc.plan'].browse(amc_id)

        if amc_plan.customer_id.id != request.env.user.partner_id.id:
            return request.redirect('/amc_overview')

        amc_history = request.env['amc.plan'].search([
            ('customer_id', '=', request.env.user.partner_id.id),
            ('sale_order_id', '=', amc_plan.sale_order_id.id)
        ])

        return request.render('bi_amc_portal.amc_plan_history_template', {
            'amc_history': amc_history,
            'amc_plan': amc_plan,
            'page_name': 'amc_history',
        })

    @http.route(['/amc_invoices/<int:amc_id>'], type='http', auth="user", website=True)
    def amc_invoices(self, amc_id, **post):
        """Invoices Page for the AMC plan."""
        amc_plan = request.env['amc.plan'].browse(amc_id)
        invoices = request.env['account.move'].sudo().search([('amc_plan_id', '=', amc_plan.id)])
        return request.render('bi_amc_portal.amc_plan_invoices_template', {
            'amc_plan': amc_plan,
            'invoices': invoices,
            'page_name': 'amc_invoices',
        })
  



  
   