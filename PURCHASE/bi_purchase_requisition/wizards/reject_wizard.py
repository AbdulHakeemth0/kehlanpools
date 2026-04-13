from odoo import api, fields, models, _


class RejectWizard(models.TransientModel):
    _name = 'reject.wizard'
    _description = 'Reject Wizard'

    initial_purchase_request_id = fields.Many2one('purchase.request', string='Initial Purchase Request')
    reject_reason = fields.Char(string='Reject Reason')
    
    
    def cancel_reason(self):
        for rec in self:
            if rec.initial_purchase_request_id:
                rec.initial_purchase_request_id.reason_for_reject = self.reject_reason
                rec.initial_purchase_request_id.is_rejected = True
                rec.initial_purchase_request_id.state = 'cancel'
