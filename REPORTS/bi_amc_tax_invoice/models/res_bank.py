from odoo import fields, models


class ResBank(models.Model):
    _inherit = "res.bank"

    bank_iban_no = fields.Char(
        string='Iban No',
    )
    swift_code = fields.Char(
        string='Swift Code',
    )
