from odoo import api, fields, models,_
from datetime import date


class AccountJOurnal(models.Model):
    _inherit = 'account.journal'

    amc_vas_type = fields.Selection([
        ('vas', 'VAS'),
        ('amc', 'AMC'),
    ], string="Type(VAS/AMC)")
