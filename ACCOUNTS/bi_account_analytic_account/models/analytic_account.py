from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    is_vas = fields.Boolean(string="Is VAS")
    is_amc = fields.Boolean(string="Is AMC")


        




