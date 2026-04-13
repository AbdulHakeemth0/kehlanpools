from odoo import models, fields


class HrContract(models.Model):
    _inherit = "hr.contract"


    overtime_amount = fields.Float(string="OvertTime Amount")