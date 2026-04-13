from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    is_petty_cash = fields.Boolean(string="Is Petty Cash Journal?", copy=False)

