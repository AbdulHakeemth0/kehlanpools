from odoo import models, fields, api, _
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta


class HrContract(models.Model):
    _inherit = "hr.contract"

    house_alw = fields.Float(string="House Allowance")
    travel_alw = fields.Float(string="Travelling Allowance")
    meal_alw = fields.Float(string="Meal Allowance")
    fuel_alw = fields.Float(string="Fuel Allowance")
    other_alw = fields.Float(string="Other Allowance")