from odoo import models, fields, api, _
from odoo.exceptions import UserError  

class PurchaseRequisitionNew(models.Model):
    _name = "purchase.requisition.new"
    _description = "Purchase Requisition New"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    

    @api.depends('pr_approved_line.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            amount = 0.0
            for line in order.pr_approved_line:
                amount += line.price_subtotal
            order.update({
                'amount_total': amount,
            })
            
    name = fields.Char('Order Reference',
                       index=True, copy=False, default='New')
    partner_ref = fields.Char('Subject', copy=False,
                              help="Reference of the sales order or bid sent by the vendor. "
                              "It's used to do the matching when you receive the "
                              "products as this reference is usually written on the "
                              "delivery order sent by your vendor.", readonly = True)
    date_order = fields.Datetime('Request Date', required=True, index=True, copy=False, readonly = True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id.id, readonly = True)
    date_end = fields.Datetime(string='Expected Order', tracking=True)
    payment_term_id = fields.Many2one('account.payment.term', 'Payment Terms')
    status_po = fields.Selection([
        ('approved', "Approved"),
        ('rfq_sent', "RFQ Sent"),
        ('rfq_approve', "RFQ Approve"),
        ('quotation_confirm', "Quotation Confirmed"),
        ('purchase_order', "To Approve PO"),
        ('purchase_approved', "PO Approved"),
        ('goods_received', "Goods Received")], default='', help="Technical field for UX purpose.", string="Purchase Status")
    # department_id = fields.Many2one('product.department', string="Department", required=False)   
    
    
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('validate', 'Validated'),
        ('approved', 'Approved'), ('cancel', 'Canceled')
    ], string='Status', index=True, copy=False, default='draft', tracking = True)
    
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)
    amount_total = fields.Monetary(
        string='Total', store=True, readonly=True, compute='_compute_amount_total')
    notes = fields.Text('Terms and Conditions')
    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Fiscal Position')
    user_id = fields.Many2one('res.users', string='Initiated By',
                              index=True, tracking = True, default=lambda self: self.env.user,readonly = True)
    submitted_user_id = fields.Many2one('res.users', string='Prepared By:')
    reviewed_user_id = fields.Many2one('res.users', string='Reviwed By:')
    approved_user_id = fields.Many2one('res.users', string='Approved By:')
    pr_approved_line = fields.One2many('purchase.requisition.new.line', 'pr_approved_id', string='PR Approved Lines', copy=True)
    vendor_id = fields.Many2many('res.partner',string="Proposed Supplier")
    # rfq_order_id = fields.Many2one('bi.purchase.order',string = "Request For Quotation")
    rfq_order_ids = fields.One2many('bi.purchase.order','requisition_id',string="Rfq order")
    m_number = fields.Char(string="M-number")
    job_number = fields.Many2one("sale.order", string="Job number")
    
    def select_line(self):
        product_list = []
        for each in self.pr_approved_line:
            if each.is_select:
                product_list.append((0, 0, {
                            'product_id': each.product_id.id,
                            'name':each.name,
                            'product_uom':each.product_uom.id,
                            'product_qty': each.product_qty,
                            'price_unit':each.price_unit,
                            'price_subtotal': each.price_subtotal,
                        }))
        partner = []
        if self.vendor_id:
            for each in self.vendor_id:
                partner.append(each.id)
            

        return {
            'type': 'ir.actions.act_window',
            'name': _("Create requisition Wizard"),
            'view_mode': 'form',
            'res_model': 'requisition.wizard',
            'target': 'new',
            'context':{
                    'default_requisition_id':self.id,
                    'default_partner_ids':partner,
                    'default_payment_term_id':self.payment_term_id.id,
                    # 'default_partner_ref' :  self.partner_ref,
                    'default_date_end': self.date_end,
                    'default_m_number':self.m_number,
                    'default_job_number':self.job_number.id,
                    'default_requisition_wiz_line_ids': product_list,
                    
                },
        }


    def button_submit(self):
        pass
        # self.submitted_user_id = self.env.user.id
        # self.write({'state': 'submit' })
        
        # for user in self:
        #     group_ids = [
        #             self.env.ref('bi_purchase_requisition.module_purchase_requisition_reviewed').id,

        #         ]
        # user_list = self.env['res.users'].search([
        #         ('groups_id', 'in', group_ids)
        #     ])
        # partner_ids = user_list.mapped('partner_id').ids
        # if partner_ids:
        #     user.message_post(
        #         body=f"Purchase Requisition {user.name} has been submitted by {self.env.user.name}. "
        #             f"Please take the necessary actions to move forward",
        #         subtype_id=self.env.ref('mail.mt_comment').id, 
        #         partner_ids=partner_ids
        #     )
        # return {}


    def button_validate(self):
        pass
        # self.reviewed_user_id = self.env.user.id
        # self.write({'state': 'validate'})
        # for user in self:
        #     group_ids = [
        #         self.env.ref('bi_purchase_requisition.module_purchase_requisition_manager').id,

        #     ]
        # user_list = self.env['res.users'].search([
        #         ('groups_id', 'in', group_ids)
        #     ])
        # partner_ids = user_list.mapped('partner_id').ids
        # if partner_ids:
        #     user.message_post(
        #         body=f"Purchase Requisition {user.name} has been validated by {self.env.user.name}. "
        #             f"Please take the necessary actions to move forward",
        #         subtype_id=self.env.ref('mail.mt_comment').id, 
        #         partner_ids=partner_ids
        #     )
        # return {}
    
    def button_reviewd(self):
        pass
        # self.state = 'reviewed'
        # for user in self:
        #     group_ids = [
        #     self.env.ref('bi_purchase_requisition.module_purchase_requisition_validate').id,

        #     ]
        # user_list = self.env['res.users'].search([
        #         ('groups_id', 'in', group_ids)
        #     ])
        # partner_ids = user_list.mapped('partner_id').ids
        # if partner_ids:
        #     user.message_post(
        #         body=f"Purchase Requisition {user.name} has been reviewed by {self.env.user.name}. "
        #             f"Please take the necessary actions to move forward",
        #         subtype_id=self.env.ref('mail.mt_comment').id, 
        #         partner_ids=partner_ids
        #     )



    def button_cancel(self):
        self.write({'state': 'cancel'})
        return {}
    
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                seq_date = None
                if "date_order" in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals["date_order"]))
                seq_number = self.env["ir.sequence"].next_by_code("purchase.requisition.new", sequence_date=seq_date) or "/"
                vals["name"] = seq_number
        res = super(PurchaseRequisitionNew, self).create(vals_list)
        for user in res:
            group_ids = [
                    self.env.ref('bi_purchase_requisition.module_purchase_requisition_user').id,
                ]
            user_list = self.env['res.users'].search([
                     ('groups_id', 'in', group_ids)
                ])
            partner_ids = user_list.mapped('partner_id').ids
            # if partner_ids:
            #     user.message_post(
            #         body=f"Purchase Requisition {user.name} has been created by {self.env.user.name}. "
            #             f"Please take the necessary actions to move forward.",
            #         subtype_id=self.env.ref('mail.mt_comment').id, 
            #         partner_ids=partner_ids
            #     )
        return res
                
                
    
  

    def button_approve(self):
        # line_list = []
        # for rec in self.pr_approved_line:
        #     if not rec.product_id:
        #         raise UserError(_("Provide Product to approve Purchase Requisition")) 
        #     line_list.append(
        #         (
        #             0,
        #             0,
        #             {
        #                 "product_id":rec.product_id.id,
        #                 "name": rec.name,
        #                 "product_qty": rec.product_qty,
        #                 "price_unit": rec.price_unit,
        #                 "price_subtotal": rec.price_subtotal,
        #                 "product_uom": rec.product_uom.id if rec.product_uom else False,
        #                 # "currency_id": rec.currency_id,

        #             },
        #         )
        #     )
            
        #     values = {
        #         # "partner_id": self.user_id.id,
        #         "vendor_id":self.vendor_id.ids,
        #         "origin":self.name,
        #         "delivery_date":self.date_end,
        #         "payment_term_id":self.payment_term_id.id,
        #         "order_line": line_list,
        #         "requisition_id":self.id,
        #     }
        # rfq_id = self.env['bi.purchase.order'].create(values)
        # rfq_id.button_submit()
        # self.rfq_order_id = rfq_id
        self.state = 'approved'
        self.status_po = 'approved'
        
        for user in self:
            group_ids = [
            self.env.ref('purchase.group_purchase_manager').id,

            ]
            user_list = self.env['res.users'].search([
                    ('groups_id', 'in', group_ids)
                ])
            partner_ids = user_list.mapped('partner_id').ids
            # if partner_ids:
            #     user.message_post(
            #         body=f"Purchase Requisition {user.name} has been approved by {self.env.user.name}. "
            #             f"Please take the necessary actions to create Purchase RFQ",
            #         subtype_id=self.env.ref('mail.mt_comment').id, 
            #         partner_ids=partner_ids
            #     )
    
    def get_rfq(self):
        return {
        "name": ("Request For Quotation"),
        "res_model": "bi.purchase.order",
        # 'res_id':requisition_id.id,
        "view_mode": "list,kanban,form",
        "type": "ir.actions.act_window",
        "domain": [("requisition_id", "=", self.id), ("state", "!=", "cancel")],
        # 'context': {'default_partner_id': self.vendor_id.id if self.vendor_id.id else False}
    }    
    
    
    
    
    
class PurchaseRequisitionNewLine(models.Model):
    _name = 'purchase.requisition.new.line'
    _description = 'Purchase Requisition New Line'

    pr_approved_id = fields.Many2one('purchase.requisition.new', string='PR Reference', index=True, required=True, ondelete='cascade')

    product_uom_qty = fields.Float(
        string='Total Quantity', store=True)

    is_select = fields.Boolean(string="Select")
    currency_id = fields.Many2one(comodel_name='res.currency', related='pr_approved_id.currency_id', store=True, string='Currency', readonly=True)
    state = fields.Selection(
        related='pr_approved_id.state', store=True, readonly=False)
    sequence = fields.Integer(string='Sequence', default=10)
    name = fields.Text(string='Description', required=True)
    product_uom = fields.Many2one('uom.uom', string='Unit of Measure')
    product_id = fields.Many2one('product.product',string = "Product")
    date_planned = fields.Datetime(
        string='Scheduled Date', required=False, index=True)
    company_id = fields.Many2one('res.company', related='pr_approved_id.company_id', string='Company', store=True, readonly=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    analytic_tag_ids = fields.Many2many(
        'account.analytic.plan', string='Analytic Tags')
    product_qty = fields.Float(string='Quantity', digits="Product Unit of Measure", required=True)
    price_unit = fields.Float(
        string='Unit Price', required=True, digits="Product Price")
    price_subtotal = fields.Monetary(
        compute='_compute_price_subtotal', string='Subtotal', store=True)
    date_order = fields.Datetime(
        related='pr_approved_id.date_order', string='PO Date', readonly=True)
    
    @api.depends('product_qty', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.update({
                'price_subtotal': line.product_qty * line.price_unit,
            })

    @api.onchange('product_id')
    def _auto_loading_uom(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.price_unit = self.product_id.standard_price
        else:
            self.product_uom = False
            self.price_unit = False