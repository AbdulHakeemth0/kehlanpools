from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal

class PaymentPortalController(portal.CustomerPortal):
    """To display customer payments in the portal"""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'account_payment_portal' in counters:
            if request.env['res.users'].browse(request.uid).partner_id.customer_rank == 1:
                values['account_payment_portal'] = request.env['account.payment'].search_count([]) \
                    if request.env['account.payment'].check_access_rights('read', raise_exception=False) else 0
                if not request.env['account.payment'].search_count([]):
                    values['account_payment_portal'] = 1
        return values

    @http.route(['/payments_overview'], type='http', auth="user", website=True)
    def payment_overview(self, **post):
        """Payments Overview Page."""
        # Fetch all payment records
        payment_records = request.env['account.payment'].search([('partner_id', '=',  request.env.user.partner_id.id)])

        return request.render('bi_payment_portal.cust_payment_overview_template', {
            'payment_records': payment_records,
            'page_name': 'payments_overview',
        })




