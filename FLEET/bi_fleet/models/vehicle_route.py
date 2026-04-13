from odoo import api, fields, models, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class VehicleRoute(models.Model):
    _name = 'vehicle.route'
    _description = 'vehicle route'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "end_point"


    start_point = fields.Char(string='Start Location', tracking=True)
    end_point = fields.Char(string='End Location', tracking=True)
