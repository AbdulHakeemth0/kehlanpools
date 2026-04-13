from odoo import models,fields,api
from num2words import num2words
 
class AccountMove(models.Model):
    _inherit = 'account.move'
    

    def amount_to_text_bi(self, amount_total):
        words = num2words(amount_total, lang='ar')
        return words