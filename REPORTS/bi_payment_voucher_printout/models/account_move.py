from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    is_voucher = fields.Boolean("Is voucher", compute="_compute_is_voucher",default=False)
    prepared_by = fields.Char("Prepared By")
    received_by = fields.Char("Received By")
    approval1_name = fields.Char("First Approver Name")
    approval2_name = fields.Char("Second Approver Name")
    approval1 = fields.Selection([
        ('finance', 'Finance Manger'),
        ('general', 'General Manager'),
        ('coo', 'Chief Operating Officer'),
        ('ceo', 'Chief executive Officer'),
    ], string="First Approval")
    approval2 = fields.Selection([
        ('finance', 'Finance Manger'),
        ('general', 'General Manager'),
        ('coo', 'Chief Operating Officer'),
        ('ceo', 'Chief executive Officer'),
    ], string="Second Approval")


    def action_voucher_report(self):
       self.ensure_one()
       return self.env.ref('bi_payment_voucher_printout.payment_voucher_report_pdf').report_action(self)


    def _compute_is_voucher(self):
        for rec in self:
            if rec.journal_id.code == 'BP' or rec.journal_id.code == 'CP':
                rec.is_voucher = True
            else:
                 rec.is_voucher = False