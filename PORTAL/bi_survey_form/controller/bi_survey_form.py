from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal

class CrmPortalController(portal.CustomerPortal):
    """CRM Portal to display and manage leads."""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'crm_lead_portal' in counters:
            values['crm_lead_portal'] = request.env['crm.lead'].search_count([]) \
                if request.env['crm.lead'].check_access_rights('read', raise_exception=False) else 0
            if not request.env['crm.lead'].search_count([]):
                values['crm_lead_portal'] = 1
        return values

    @http.route(['/crm/leads'], type='http', auth="user", website=True)
    def crm_leads(self, **post):
        """Display all leads"""
        leads = request.env['crm.lead'].search([('user_id', '=', request.env.user.id)])
        return request.render('bi_survey_form.crm_leads_template', {
            'leads': leads,
            'page_name': 'crm_leads',
        })

    @http.route(['/crm/leads/create'], type='http', auth="user", website=True)
    def crm_create_lead(self, **post):
        """Render the lead creation form."""
        mep_equipments= request.env['mep.equipment'].sudo().search([])
        customer_id= request.env['res.partner'].sudo().search([])
        return request.render('bi_survey_form.crm_site_survey_form', {
            'page_name': 'crm_lead_create',
            'mep_equipments': mep_equipments,
            'customer_id': customer_id,
        })

    @http.route('/crm/site_survey/submit', type='http', auth='user', website=True)
    def submit_site_survey_form(self, **post):
        crm_pool=request.env['crm.lead'].sudo().create({
            'name': post.get('project_ref_no'),
            'partner_id': post.get('customer_id'),
            'phone': post.get('mob_no'),
        })

        new_lines_count = 0
        slno = 1
        for key in post:
            if key.startswith('dimension_length_'):
                index = key.split('_')[-1]
                dimension_length = post.get(f'dimension_length_{index}')
                dimension_width = post.get(f'dimension_width_{index}')
                dimension_depth = post.get(f'dimension_depth_{index}')
                if dimension_length and dimension_width and dimension_depth:
                    try:
                        request.env['pool.dimension'].sudo().create({
                            'pool_dimension_sl_no': slno,
                            'length': dimension_length,
                            'breadth': dimension_width,
                            'pool_depth': dimension_depth,
                            'crm_pool_dimension_id': crm_pool.id,
                        })
                        new_lines_count += 1
                        request.env['pool.specification.line'].sudo().create({
                            'pool_specification_sl_no': slno,
                            'crm_pool_specification_id': crm_pool.id,
                        })
                        new_lines_count += 1
                        slno += 1
                    except ValueError:
                        pass

        new_lines_count = 0
        for key in post:
            if key.startswith('dimension_length_'):
                index = key.split('_')[-1]
                mep_equipments = post.get(f'mep_equipments{index}')
                equipment_make = post.get(f'equipment_make{index}')
                equipment_qty = post.get(f'equipment_qty{index}')
                equipment_type = post.get(f'equipment_type{index}')
                equipment_size = post.get(f'equipment_size{index}')
                if mep_equipments and equipment_make and equipment_qty and equipment_type and equipment_size :
                    try:
                        request.env['mep.equipment.specifications'].sudo().create({
                            'equipment_id': mep_equipments,
                            'equipment_make': equipment_make,
                            'equipment_qty': equipment_qty,
                            'equipment_type': equipment_type,
                            'equipment_size': equipment_size,
                            'crm_mep_equipment_id': crm_pool.id,
                        })
                        new_lines_count += 1
                    except ValueError:
                        pass


        return request.redirect('/crm/leads')




            # if post.get('mep_equipment_2'):
            #     mep_equipment_2 = post.get(f'mep_equipment_2')
            #     equipment_2_make = post.get(f'equipment_2_make')
            #     equipment_2_qty = post.get(f'equipment_2_qty')
            #     equipment_2_type = post.get(f'equipment_2_type')
            #     equipment_2_size = post.get(f'equipment_2_size')

            #     if post.get('mep_equipment_3'):
            #         mep_equipment_3 = post.get(f'mep_equipment_3')
            #         equipment_3_make = post.get(f'equipment_3_make')
            #         equipment_3_qty = post.get(f'equipment_3_qty')
            #         equipment_3_type = post.get(f'equipment_3_type')
            #         equipment_3_size = post.get(f'equipment_3_size')

            #         if post.get('mep_equipment_4'):
            #             mep_equipment_4 = post.get(f'mep_equipment_4')
            #             equipment_4_make = post.get(f'equipment_4_make')
            #             equipment_4_qty = post.get(f'equipment_4_qty')
            #             equipment_4_type = post.get(f'equipment_4_type')
            #             equipment_4_size = post.get(f'equipment_4_size')

            #             if post.get('mep_equipment_5'):
            #                 mep_equipment_5 = post.get(f'mep_equipment_5')
            #                 equipment_5_make = post.get(f'equipment_5_make')
            #                 equipment_5_qty = post.get(f'equipment_5_qty')
            #                 equipment_5_type = post.get(f'equipment_5_type')
            #                 equipment_5_size = post.get(f'equipment_5_size')

            #                 if post.get('mep_equipment_6'):
            #                     mep_equipment_6 = post.get(f'mep_equipment_2')
            #                     equipment_6_make = post.get(f'equipment_6_make')
            #                     equipment_6_qty = post.get(f'equipment_6_qty')
            #                     equipment_6_type = post.get(f'equipment_6_type')
            #                     equipment_6_size = post.get(f'equipment_6_size')

            #                     if post.get('mep_equipment_7'):
            #                         mep_equipment_7 = post.get(f'mep_equipment_7')
            #                         equipment_7_make = post.get(f'equipment_7_make')
            #                         equipment_7_qty = post.get(f'equipment_7_qty')
            #                         equipment_7_type = post.get(f'equipment_7_type')
            #                         equipment_7_size = post.get(f'equipment_7_size')

            #                         if post.get('mep_equipment_8'):
            #                             mep_equipment_8 = post.get(f'mep_equipment_8')
            #                             equipment_8_make = post.get(f'equipment_8_make')
            #                             equipment_8_qty = post.get(f'equipment_8_qty')
            #                             equipment_8_type = post.get(f'equipment_8_type')
            #                             equipment_8_size = post.get(f'equipment_8_size')

            #                             if post.get('mep_equipment_9'):
            #                                 mep_equipment_9 = post.get(f'mep_equipment_9')
            #                                 equipment_9_make = post.get(f'equipment_9_make')
            #                                 equipment_9_qty = post.get(f'equipment_9_qty')
            #                                 equipment_9_type = post.get(f'equipment_9_type')
            #                                 equipment_9_size = post.get(f'equipment_9_size')

            #                                 if post.get('mep_equipment_10'):
            #                                     mep_equipment_10 = post.get(f'mep_equipment_10')
            #                                     equipment_10_make = post.get(f'equipment_10_make')
            #                                     equipment_10_qty = post.get(f'equipment_10_qty')
            #                                     equipment_10_type = post.get(f'equipment_10_type')
            #                                     equipment_10_size = post.get(f'equipment_10_size')







