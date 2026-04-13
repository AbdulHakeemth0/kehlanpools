from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_miscellaneous = fields.Boolean(string="Is Salary Advance", copy=False)