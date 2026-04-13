from odoo import models, fields 


class AccountMoveLine(models.Model):
    
    _inherit = 'account.move.line'
    
    
    blocked = fields.Boolean(
        string='No Follow-up',
        default=False,
        help="You can check this box to mark this journal item as a litigation with the "
             "associated partner",
    )