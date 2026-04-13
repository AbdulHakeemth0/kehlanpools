from odoo import models, fields, api, _ 
from odoo.exceptions import UserError  

class BiPurchaseQuotation(models.Model):
    _name = "bi.purchase.quotation"
    _description = "BI Purchase Quotation"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    # bi.purchase.quotation
    
    @api.depends("quotation_line.price_total")
    def _compute_amount_all(self):
        tax_percentage = 0.0
        amount_total = 0.0
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.quotation_line:
                amount_untaxed = line.price_subtotal
                amount_total += line.price_subtotal
                for tax in line.taxes_id:
                    tax_percentage = tax.amount
                    amount_tax += amount_untaxed * (tax_percentage)/100
            order.update(
                {
                    "amount_untaxed": order.currency_id.round(amount_total),
                    "amount_tax": order.currency_id.round(amount_tax),
                    "amount_total": amount_total + amount_tax,
                }
            )


    name = fields.Char(string="PQ Number", default="New", copy=False)
    m_number = fields.Char(string="M-number")
    job_number = fields.Many2one("sale.order", string="Job number")

    partner_id = fields.Many2one("res.partner", string="Supplier ", required=True)
    origin = fields.Char(string="RFQ Number")
    partner_ref = fields.Char(string="Supplier Reference", copy=False)
    revised_count = fields.Integer(string="Revised Count",default=0,copy=False)
    old_name = fields.Char('Old name',default='none', copy=False)
    date_order = fields.Datetime(
        "PQ Date",
        index=True,
        copy=False,
        default=fields.Datetime.now,
        help="Depicts the date where the Quotation should be validated and converted into a purchase order.",
        required=True,
    )
    company_id = fields.Many2one("res.company", "Company", index=True, default=lambda self: self.env.company.id)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirm"),
            ("quotation", "Quotation Approve"),
            ("purchase", "Purchase Order"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="draft",
        tracking=True,
    )
    quotation_line = fields.One2many("bi.purchase.quotation.line", "quotation_id", string="Purchase Order Line")
    currency_id = fields.Many2one("res.currency", "Currency", default=lambda self: self.env.company.currency_id.id)
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount", store=True, readonly=True, compute="_compute_amount_all", tracking=True
    )
    amount_tax = fields.Monetary(string="Taxes", store=True, readonly=True, compute="_compute_amount_all")
    amount_total = fields.Monetary(string="Total", store=True, readonly=True, compute="_compute_amount_all")
    notes = fields.Text("Terms and Conditions")
    user_id = fields.Many2one(
        "res.users",
        string="Initiated By",
        index=True,
        tracking=True,
        default=lambda self: self.env.user,
        check_company=True,
    )
    # delivery_name = fields.Char(string='Name')
    employee_id = fields.Many2one("hr.employee", string="Employee")
    mob = fields.Char(string="Mobile")
    # attention = fields.Char(string='Attention')
    # contact_ids = fields.Many2many("res.partner", string="Contact")
    is_grn = fields.Boolean(string="Is Grn", default=False)
    is_po_mail = fields.Boolean(string="Is PO mail", default=False)
    is_rfq_mail = fields.Boolean(string="Is RFQ Mail", default=False)
    delivery_date = fields.Date(string="Delivery Date")
    requisition_id = fields.Many2one("purchase.requisition", string="Purchase Requisition")
    prepared_by_user_id = fields.Many2one("res.users", string="Prepared By:")
    approved_by_user_id = fields.Many2one("res.users", string="Approved By:")
    payment_term_id = fields.Many2one(
        "account.payment.term",
        "Payment Terms",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    pos = fields.Integer(compute="_calc_po")
    purchase_id = fields.Many2one('purchase.order',string = "Purchase Order")
    
    bi_purchase_id = fields.Many2one('bi.purchase.order', string = "bi purchase order")
    
    
    
    def confirm_quotation(self):
        pass
        # self.user_id = self.env.user.id
        # self.write({'state': 'confirm' })
        # for order in self:
        #     group_ids = [
        #     self.env.ref('bi_purchase_requisition.group_quotation_approve_1').id,

        #     ]
        #     user_list = self.env['res.users'].search([
        #             ('groups_id', 'in', group_ids)
        #         ])
        #     partner_ids = user_list.mapped('partner_id').ids
        #     if partner_ids:
        #         order.message_post(
        #             body=f"Purchase Quotation {order.name} has been confirm by {self.env.user.name}. "
        #                 f"Please take the necessary actions to move forward",
        #             subtype_id=self.env.ref('mail.mt_comment').id, 
        #             partner_ids=partner_ids
        #         )
        # return {}


    def action_approve(self):
        pass  
        # self.approved_by_user_id = self.env.user.id
        # self.write({'state': 'quotation'})
        # for order in self:
        #     group_ids = [
        #     self.env.ref('bi_purchase_requisition.group_quotation_approve_2').id,

        #     ]
        # user_list = self.env['res.users'].search([
        #         ('groups_id', 'in', group_ids)
        #     ])
        # partner_ids = user_list.mapped('partner_id').ids
        # if partner_ids:
        #     order.message_post(
        #         body=f"Purchase Quotation {order.name} has been approved by {self.env.user.name}. "
        #             f"Please take the necessary actions to move forward",
        #         subtype_id=self.env.ref('mail.mt_comment').id, 
        #         partner_ids=partner_ids
        #     )
        # return {}
       
            
    
    def action_approve_2nd(self):
        # if self.env.user.has_group('bi_purchase_requisition.group_quotation_approve_2'):
        self.approved_by_user_id = self.env.user.id
        self.write({'state': 'quotation_2'})
        for order in self:
            group_ids = [
                self.env.ref('purchase.group_purchase_manager').id,

                ]
        user_list = self.env['res.users'].search([
                ('groups_id', 'in', group_ids)
            ])
        partner_ids = user_list.mapped('partner_id').ids
        # if partner_ids:
        #     order.message_post(
        #         body=f"Purchase Quotation {order.name} has been secondarily approved by {self.env.user.name}. "
        #             f"Please take the necessary actions to move forward",
        #         subtype_id=self.env.ref('mail.mt_comment').id, 
        #         partner_ids=partner_ids
        #     )
        return {}    
        # else:
        #     raise UserError(_("Please Contact Purchase second approver to approve this quotation"))
    
    def action_cancel(self):
        self.state = 'cancel'
        
        
    def send_rfq_bymail(self):
        self.ensure_one()
        self.env.context.get("lang")
        template_id = self.env["mail.template"].search([("name", "=", "Purchase Quotation Send")])
        ctx = {
            "default_model": "bi.purchase.quotation",
            "default_res_ids": self.ids,
            "default_template_id": template_id.id,
            "default_bi_purchase_id": self.id,
            "default_composition_mode": "comment",
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }    
    



    def set_to_draft(self):
        self.write({'state': 'draft'})
        return {}
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                seq_date = None
                if "date_order" in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals["date_order"]))
                seq_number = self.env["ir.sequence"].next_by_code("bi.purchase.quotation", sequence_date=seq_date) or "/"
                vals["name"] = seq_number
            
        res = super(BiPurchaseQuotation, self).create(vals_list)      
        # for user in res:    
        #     group_ids = [
        #          self.env.ref('bi_purchase_requisition.purchase_quotation_user').id,
        #         self.env.ref('bi_purchase_requisition.purchase_quotation_manager').id,
        #         ]
        #     user_list = self.env['res.users'].search([
        #             ('groups_id', 'in', group_ids)
        #         ])
        #     partner_ids = user_list.mapped('partner_id').ids
        #     if partner_ids:
        #         user.message_post(
        #             body=f"Purchase Quotation {user.name} has been created by {self.env.user.name}. "
        #                 f"Please take the necessary actions to move forward.",
        #             subtype_id=self.env.ref('mail.mt_comment').id, 
        #             partner_ids=partner_ids
        #         )          
        return res
    
    
    

    def action_create_po(self):
        line_list = []
        for rec in self.quotation_line:
            line_list.append(
                (
                    0,
                    0,
                    {
                        "product_id":rec.product_id.id,
                        "product_qty": rec.product_qty,
                        "product_uom":rec.product_uom.id,
                        "price_unit":rec.price_unit,
                        "taxes_id":rec.taxes_id.ids,
                        "discount":rec.discount,
                       
                        # "price_subtotal": rec.price_subtotal,
                        # "currency_id": rec.currency_id,

                    },
                )
            )
            
            values = {
                "partner_id": self.partner_id.id,
                "partner_ref":self.partner_ref,
                "origin":self.name,
                "date_planned":self.delivery_date,
                "order_line": line_list,
                "bi_purchase_quotation_id":self.id,
                # "payment_term_id":self.payment_term_id,
            }
        purchase_id = self.env['purchase.order'].create(values)
        # rfq_id.button_submit()
        self.purchase_id = purchase_id
        self.state = 'purchase'
        self.bi_purchase_id.requisition_id.write({"status_po": "purchase_order"})

        
    def get_purchase_order(self):
        return {
        "name": ("Purchase Order"),
        "res_model": "purchase.order",
        # 'res_id':requisition_id.id,
        "view_mode": "list,form",
        "type": "ir.actions.act_window",
        "domain": [("id", "=", self.purchase_id.id), ("state", "!=", "cancel")],
        # 'context': {'default_partner_id': self.vendor_id.id if self.vendor_id.id else False}
    }    
    
    
class BiPurchaseQuotationLine(models.Model):
    _name = "bi.purchase.quotation.line"
    _description = "BI Purchase Quotation Line"
    _inherit = ["mail.thread"]

    quotation_id = fields.Many2one("bi.purchase.quotation", string="Purchase Order")
    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Text(string="Description", required=True)
    product_id = fields.Many2one(
        "product.product", string="Product", domain=[("purchase_ok", "=", True)], change_default=True
    )
    product_qty = fields.Float(string="Quantity", digits="Product Unit of Measure", required=True)
    product_uom_qty = fields.Float(string="Total Quantity", compute="_compute_product_uom_qty", store=True)
    price_unit = fields.Float(string="Unit Price", digits="Product Price")
    discount = fields.Float(string="Discount (%)", digits="Discount", default=0.0)
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure", required=True)
    product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    taxes_id = fields.Many2many("account.tax", string="Taxes", domain=[("type_tax_use", "=", "purchase")])
    # taxes_id = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Monetary(compute="_compute_price_subtotal", string="Subtotal", store=True)
    price_total = fields.Monetary(compute="_compute_price_subtotal", string="Total", store=True)
    # price_tax = fields.Float(compute="_compute_amount", string="Tax", store=True)
    currency_id = fields.Many2one(related="quotation_id.currency_id", store=True, string="Currency", readonly=True)
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")], default=False, help="Technical field for UX purpose."
    )
    date_planned = fields.Datetime(string="Scheduled Date", index=True)
    state = fields.Selection(
        string="Status",
        related="quotation_id.state",
        readonly=True,
        index=True,
        copy=False,
        tracking=True,
        store=True,
    )
    
    
    @api.depends('product_qty', 'price_unit','discount')
    def _compute_price_subtotal(self):
        discount_amount = 0
        for line in self:
            if line.discount:
                discount_amount = ((line.product_qty * line.price_unit)*line.discount)/100
            else:
                discount_amount = 0   
                
            line.update({
                'price_subtotal': (line.product_qty * line.price_unit) - discount_amount,
            })
    
    # @api.depends('product_qty', 'price_unit')
    # def _compute_price_subtotal(self):
    #     for line in self:
    #         line.update({
    #             'price_subtotal': line.product_qty * line.price_unit,
    #         })
    
