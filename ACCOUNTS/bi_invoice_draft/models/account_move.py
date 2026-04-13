from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def set_draft_invoice(self):
        invoice = self.env["account.move"].browse(self._context.get("active_ids")) 
        for each in invoice:
            each.button_draft()   
                            