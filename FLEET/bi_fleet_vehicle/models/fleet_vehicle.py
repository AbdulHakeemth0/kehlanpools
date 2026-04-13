from odoo import api, fields, models, _
from lxml import etree

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    team_lead_id = fields.Many2one('hr.employee',string="Team Lead", domain=[("is_team_lead", "=", True)])
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    route_id = fields.Many2one("vehicle.route",string="vehicle Route")

                
    def damage_history(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vehicle Damage History',
            'view_mode': 'list',
            'res_model': 'fleet.vehicle.damages.history',
            'domain': [('model_id', '=', self.model_id.id)],
            'context': {
                'search_default_groupby_view_type': True,
            }
        }
    
    def write(self, vals):
        res = super().write(vals)
        if 'image_1_damage_ids' in vals:
            for each in self.image_1_damage_ids:
                data = {
                       "date": each.date,
                       "name": each.name,
                       "comments": each.comments,
                       "fleet_id":self.id,
                       "view_type":'front',
                       "model_id":self.model_id.id
            }
            self.env['fleet.vehicle.damages.history'].sudo().create(data)
        if 'image_2_damage_ids' in vals:
            for each in self.image_2_damage_ids:
                data = {
                       "date": each.date,
                       "name": each.name,
                       "comments": each.comments,
                       "fleet_id":self.id,
                       "view_type":'right',
                       "model_id":self.model_id.id
            }
            self.env['fleet.vehicle.damages.history'].sudo().create(data)
        if 'image_3_damage_ids' in vals:
            for each in self.image_3_damage_ids:
                data = {
                       "date": each.date,
                       "name": each.name,
                       "comments": each.comments,
                       "fleet_id":self.id,
                       "view_type":'left',
                       "model_id":self.model_id.id
            }
            self.env['fleet.vehicle.damages.history'].sudo().create(data)
        if 'image_4_damage_ids' in vals:
            for each in self.image_4_damage_ids:
                data = {
                       "date": each.date,
                       "name": each.name,
                       "comments": each.comments,
                       "fleet_id":self.id,
                       "view_type":'rear',
                       "model_id":self.model_id.id
            }
            self.env['fleet.vehicle.damages.history'].sudo().create(data)
        if 'team_lead_id' in vals:
            lead_id = vals['team_lead_id']
            self.create_driver_history_form(vals)
        return res
    
    @api.model_create_multi
    def create(self, vals_list):
        vehicles = super(FleetVehicle, self).create(vals_list)
        for vals in vehicles:
            if 'team_lead_id' in vals and vals['team_lead_id']:
                self.create_driver_history_form(vals)
        return vehicles
    
    def create_driver_history_form(self, vals):
        if not self:
            for vehicle in  vals:
                self.env['fleet.vehicle.assignation.log'].create(vehicle._get_driver_history_datas(vals),)
        else:
            for vehicle in self:
                self.env['fleet.vehicle.assignation.log'].create(vehicle._get_driver_history_datas(vals),)
    

    def _get_driver_history_datas(self, vals):
        self.ensure_one()
        return {
            'vehicle_id': self.id,
            'driver_employee_id':self.team_lead_id.id,
            'date_start': self.date_from,
            'date_end':self.date_to
        }



class FleetVehicleAssignationLog(models.Model):
    _inherit = "fleet.vehicle.assignation.log"
  
    driver_id = fields.Many2one('res.partner', string="Driver", required=False)


   

  
