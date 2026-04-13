# -*- coding: utf-8 -*-
from odoo import models, fields


class BiOvertime(models.Model):
    _name = 'bi.overtime'
    _description = 'Overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "number"

    overtime_type = fields.Selection([
        ('normal_ot', 'Normal OT'),
        ('holiday_ot', 'Holiday OT'),
    ], default='normal_ot', string='Overtime Type', tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    ot_hours = fields.Float(string='OT Hours', tracking=True)
    first_check_in = fields.Datetime(string='First Check In', tracking=True)
    last_check_out = fields.Datetime(string='Last Check Out', tracking=True)
    overtime_pay = fields.Float(string='Overtime Pay', tracking=True)
    number=fields.Char(string='number')
