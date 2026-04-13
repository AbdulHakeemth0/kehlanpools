from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError 

class RejectReason(models.TransientModel):
    _name ='reject.reason.wizard'
    _description ='Reject Reason'
    
    
    reason = fields.Char(string = 'Reason')
    sale_order_id = fields.Many2one("sale.order", string="Sale Order")
    
    
    
    def button_reject_submit(self):
        for vals in self:
            if not vals.reason:
                raise UserError(_("Please enter the reason"))
            current_user = self.env.user
            vals.sale_order_id.reject_reason = vals.reason, 
            vals.sale_order_id.rejected_by = current_user.id
            vals.sale_order_id.state = "draft"