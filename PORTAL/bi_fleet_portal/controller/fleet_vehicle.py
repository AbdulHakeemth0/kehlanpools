from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal
from datetime import datetime

class FleetPortalController(portal.CustomerPortal):
    """To display fleet vehicles in the portal"""

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'fleet_vehicle_portal' in counters:
            if request.env['res.users'].browse(request.uid).employee_id:
                if request.env['res.users'].browse(request.uid).employee_id.is_team_lead:
                    values['fleet_vehicle_portal'] = request.env['fleet.vehicle'].search_count([]) \
                        if request.env['fleet.vehicle'].check_access_rights('read', raise_exception=False) else 0
                    if not request.env['fleet.vehicle'].search_count([]):
                        values['fleet_vehicle_portal'] = 1
        return values

    @http.route(['/fleet_overview'], type='http', auth="user", website=True)
    def fleet_overview(self, **post):
        """Fleet Overview Page."""
        fleet_records = request.env['fleet.vehicle'].sudo().search([('team_lead_id.user_id', '=', request.uid)])
        # emps = request.env['hr.employee'].sudo().search([('user_id', '=', request.uid)])

        return request.render('bi_fleet_portal.fleet_overview_template', {
            'fleet_records': fleet_records,
            'page_name': 'fleet_overview',
            # 'employee':emps
        })
    

    @http.route(['/fleet_view/form<int:id>'], type='http', auth="user", website=True)
    def review_your_fleet(self,id, **kw):
        user = request.env['res.users'].browse(request.uid)
        employee = request.env['hr.employee'].sudo().search([('user_id','=',user.id)])
        fleet = request.env['fleet.vehicle'].sudo().browse(id)
        if fleet.exists():
                return request.render('bi_fleet_portal.fleet_portal_form', {
                'page_name': 'fleet_overview',
                'fleet_records': fleet,
            })
        
    @http.route(['/my/fleet_view_controller'], type='http', auth="public", website=True)
    def create_odometer_record(self, **post):
        fleet_id = post.get('fleet_id')
        if fleet_id:
            fleet_id = int(post.get('fleet_id'))
            fleet_record = request.env['fleet.vehicle'].sudo().browse(fleet_id)

            if not fleet_record.exists():
                return request.redirect('/fleet_overview')  

            vehicle_odometer = request.env['fleet.vehicle.odometer'].sudo().search([
                ('vehicle_id', '=', fleet_record.id)
            ])

            if vehicle_odometer:
                for rec in vehicle_odometer:
                    id_in = 'id_%d' % rec.id
                    odometer_rec = request.env['fleet.vehicle.odometer'].sudo().browse(int(id_in[3:]))
                    existing_odometer_vals = {
                        'date': odometer_rec.date,
                        'starting_odometer_value': odometer_rec.starting_odometer_value,
                        'ending_odometer_value': odometer_rec.ending_odometer_value,
                    }
                    date_key = 'date_%d' % odometer_rec.id
                    start_km_key = 'starting_km_%d' % odometer_rec.id
                    end_km_key = 'ending_km_%d' % odometer_rec.id

                    if date_key in post and post[date_key] != existing_odometer_vals['date']:
                        odometer_rec.sudo().write({'date': post[date_key]})
                    if start_km_key in post and post[start_km_key] != existing_odometer_vals['starting_odometer_value']:
                        odometer_rec.sudo().write({'starting_odometer_value': float(post[start_km_key])})
                    if end_km_key in post and post[end_km_key] != existing_odometer_vals['ending_odometer_value']:
                        odometer_rec.sudo().write({'ending_odometer_value': float(post[end_km_key])})


            for key in post:
                if key.startswith('date_'):
                    index = key.split('_')[-1]
                    odometer_id_key = f'date_{index}'
                    date_ = datetime.strptime(post[odometer_id_key], "%Y-%m-%d")
                    # odometer_id = odometer_key.strftime("%Y-%m-%d")
                    if odometer_id_key in post and post[odometer_id_key]:
                        odometer_rec = request.env['fleet.vehicle.odometer'].sudo().browse(int(index))
                        if odometer_rec.exists():
                            update_vals = {
                                'date': date_,
                                'vehicle_id':int(post.get('fleet_id')),
                                'starting_odometer_value': float(post.get(f'starting_km_{index}', odometer_rec.starting_odometer_value)),
                                'ending_odometer_value': float(post.get(f'ending_km_{index}', odometer_rec.ending_odometer_value)),
                            }
                            odometer_rec.sudo().write(update_vals)
                        else:
                            odometer_vals = {
                                'date': post.get(f'date_{index}'),
                                'vehicle_id': fleet_record.id,
                                'driver_employee_id': fleet_record.team_lead_id.id,
                                'starting_odometer_value': float(post.get(f'starting_km_{index}', 0)),
                                'ending_odometer_value': float(post.get(f'ending_km_{index}', 0)),
                            }
                            request.env['fleet.vehicle.odometer'].sudo().create(odometer_vals)

            return request.redirect('/fleet_overview')

