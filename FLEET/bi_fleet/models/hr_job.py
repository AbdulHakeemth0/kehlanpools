from odoo import api, fields, models, _

class Job(models.Model):
    _inherit = "hr.job"

    is_fleet_visible = fields.Boolean(tracking=True)
