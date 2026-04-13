from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'res.users'


    digital_sign = fields.Binary(string="Digital Sign")