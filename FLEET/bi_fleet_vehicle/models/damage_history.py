from datetime import datetime, date, timedelta
from odoo import api, fields, models, _

class FleetVehicleDamagesHistory(models.Model):
    _name = 'fleet.vehicle.damages.history'
    _description = 'Fleet Vehicle Damages History'

    
    date = fields.Date(string="Date")
    name = fields.Char(string='Name')
    comments = fields.Text(string='Comments')
    fleet_id = fields.Many2one('fleet.vehicle')
    view_type = fields.Selection([
        ('front', 'Front View'),
        ('right', 'Right Side View'),
        ('left', 'Left Side View'),
        ('rear', 'Rear View'),
    ], string="View Type", required=True)
    model_id = fields.Many2one('fleet.vehicle.model')



