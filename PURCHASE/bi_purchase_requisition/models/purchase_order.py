from odoo import models, fields, api 

class PurchaseOrder(models.Model):
    
    _inherit = "purchase.order"
    
    bi_custom_state = fields.Char(string="Bi Custom State")
    material_req_id = fields.Many2one('bi.purchase.order',string = "Material Request")
    attention = fields.Char(string="Attention")
    mr_remarks = fields.Text(string="MR Remarks")
    bi_purchase_quotation_id = fields.Many2one('bi.purchase.quotation',string = "Purchase quotation")
    m_number = fields.Char(string="M-Number")
    job_number = fields.Many2one('sale.order',string="Job Number")
    
    def button_confirm(self):
        res = super(PurchaseOrder,self).button_confirm()
        for rec in self:
           if rec.bi_purchase_quotation_id:
               rec.bi_purchase_quotation_id.bi_purchase_id.requisition_id.write({"status_po": "purchase_approved"}) 
        return res
    
    
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(PurchaseOrder, self).create(vals_list)      
        for user in res:
            group_ids = [
                self.env.ref('purchase.group_purchase_manager').id,

            ]
        user_list = self.env['res.users'].search([
                ('groups_id', 'in', group_ids)
            ])
        partner_ids = user_list.mapped('partner_id').ids
        # if partner_ids:
        #     user.message_post(
        #         body=f"purchase request {user.name} has been created by {self.env.user.name}. "
        #             f"Please take the necessary actions for Purchase Order.",
        #         subtype_id=self.env.ref('mail.mt_comment').id, 
        #         partner_ids=partner_ids
        #     )     

        return res
    
    def print_rfq(self):
        return self.env.ref('purchase.report_purchase_quotation').report_action(self)

    def print_po(self):
        return self.env.ref('bi_purchase_order_report.purchase_order_report_action').report_action(self)
    
class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    discount = fields.Float(
        string="Discount (%)",
        compute='_compute_price_unit_and_date_planned_and_name',
        digits=(16, 20),
        store=True, readonly=False)