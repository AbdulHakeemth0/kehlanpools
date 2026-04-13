from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError


class BiPurchaseOrder(models.Model):
    _name = "bi.purchase.order"
    _description = "BI Purchase Order"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    
    @api.depends("order_line.price_total")
    def _compute_amount_all(self):
        tax_percentage = 0.0
        amount_total = 0.0
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
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


    name = fields.Char(string="Requisition Number", default="New", copy=False)
    user_id = fields.Many2one(
        "res.users",
        string="Initiated By",
        index=True,
        tracking=True,
        default=lambda self: self.env.user,
    )
    m_number = fields.Char(string="M-number")
    job_type = fields.Selection([
        ('job', 'JOB'),
        ('consumable', 'CONSUMABLE'),
    ], string="Type")
    job_number = fields.Many2one("sale.order", string="Job number")
    requested_by = fields.Char(string="Requested By")
    partner_id = fields.Many2one("res.partner", string="Requested")
    origin = fields.Char(string="Requisition Number ")
    partner_ref = fields.Char(string="Supplier Reference", copy=False)
    revised_count = fields.Integer(string="Revised Count",default=0,copy=False)
    old_name = fields.Char('Old name',default='none', copy=False)
    date_order = fields.Datetime(
        "RFQ Date",
        index=True,
        copy=False,
        default=fields.Datetime.now,
        help="Depicts the date where the Quotation should be validated and converted into a purchase order.",
        required=True,
    )
    company_id = fields.Many2one("res.company", "Company", index=True, default=lambda self: self.env.company.id)
    state = fields.Selection(
        [
            ("draft", "MR"),
            ("confirm", "To Approve"),
            ("approve", "Request Approved"),
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
    order_line = fields.One2many("bi.purchase.order.line", "order_id", string="Purchase Order Line")
    currency_id = fields.Many2one("res.currency", "Currency", default=lambda self: self.env.company.currency_id.id)
    amount_untaxed = fields.Monetary(
        string="Untaxed Amount", store=True, readonly=True, compute="_compute_amount_all"
    )
    amount_tax = fields.Monetary(string="Taxes", store=True, readonly=True, compute="_compute_amount_all")
    amount_total = fields.Monetary(string="Total", store=True, readonly=True, compute="_compute_amount_all")
    notes = fields.Text("Remarks")
    user_id = fields.Many2one(
        "res.users",
        string="Initiated By",
        index=True,
        tracking=True,
        default=lambda self: self.env.user,
        check_company=True,
    )
    # delivery_name = fields.Char(string='Name')
    employee_id = fields.Many2one("hr.employee", string="Name")
    mob = fields.Char(string="Mobile")
    # attention = fields.Char(string='Attention')
    # contact_ids = fields.Many2many("res.partner", string="Contact")
    is_grn = fields.Boolean(string="Is Grn", default=False)
    is_po_mail = fields.Boolean(string="Is PO mail", default=False)
    is_rfq_mail = fields.Boolean(string="Is RFQ Mail", default=False)
    delivery_date = fields.Date(string="Expecting Delivery Date")
    requisition_id = fields.Many2one("purchase.requisition.new", string="Purchase Requisition")
    prepared_by_user_id = fields.Many2one("res.users", string="Prepared By:")
    approved_by_user_id = fields.Many2one("res.users", string="Approved By:")
    payment_term_id = fields.Many2one(
        "account.payment.term",
        "Payment Terms",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    pos = fields.Integer(compute="_calc_po")
    
    vendor_id = fields.Many2many('res.partner',string = "Supplier")
    
    bi_purchase_quotation_ids = fields.One2many('bi.purchase.quotation','bi_purchase_id',string="purchase quotation")
    
    def confirm_rfq(self):
        if not self.order_line:
            raise ValidationError(_("Please provide product details..."))
        else:
            group_ids = [
            self.env.ref('bi_purchase_requisition.purchase_rfq_manager').id,]
            user_list = self.env['res.users'].search([
                            ('groups_id', 'in', group_ids)
                        ])
            # for each_user in user_list:
            #     usr_id = each_user.id
            #     model = self.env["ir.model"].sudo().search([("model", "=", "bi.purchase.order")])     
            #     data = {
            #         "res_id": self.id,
            #         "res_model_id": model.id,
            #         "user_id": usr_id,
            #         "summary": _(('Material request has been sent by-%s') % (
            #                         str(self.user_id.name))),
            #         "activity_type_id": self.env.ref("bi_purchase_requisition.material_request_id").id
            #     }
            #     self.env["mail.activity"].sudo().create(data)
            self.state = 'confirm'
        #         self.requisition_id.write({"status_po": "rfq_sent"})
        # if not self.order_line.product_uom and not self.order_line.taxes_id:
        #     raise UserError(_("Please select the UOM and Tax"))
        # else:
        #     if self.requisition_id and self.requisition_id.status_po != "purchase_order":
        #         self.requisition_id.write({"status_po": "rfq_sent"})
        #     for order in self:
        #         order.state = "confirm"
        #         order.prepared_by_user_id = self.env.user.id
                
        #         group_ids = [
        #         self.env.ref('bi_purchase_requisition.purchase_rfq_user').id,

        #         ]
        #         user_list = self.env['res.users'].search([
        #                 ('groups_id', 'in', group_ids)
        #             ])
        #         partner_ids = user_list.mapped('partner_id').ids
        #         if partner_ids:
        #             order.message_post(
        #                 body=f"Purchase RFQ {order.name} has been confirm by {self.env.user.name}. "
        #                     f"Please take the necessary actions to move forward",
        #                 subtype_id=self.env.ref('mail.mt_comment').id, 
        #                 partner_ids=partner_ids
        #             )
        
    @api.model
    def search_fetch(self, domain=None, field_names=None, offset=0, limit=None, order=None):
        if domain is None:
            domain = [('user_id', '=', self.env.user.id)]
        user_employee = self.env.user.employee_id    
        if not self.env.user.has_group('bi_purchase_requisition.purchase_rfq_manager'):
            domain += [('user_id', '=', self.env.user.id)] 
        return super(BiPurchaseOrder, self).search_fetch(domain, field_names, offset, limit, order)
    


    def action_approve(self):
        self.approved_by_user_id = self.env.user.id
        self.approved_by = self.env.user.id
        self.state = "approve"
        self.requisition_id.write({"status_po": "rfq_approve"})
        # self.create_grn()
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
            #         body=f"Purchase RFQ {user.name} has been approved by {self.env.user.name}. "
            #             f"Please take the necessary actions to create Purchase Quotation",
            #         subtype_id=self.env.ref('mail.mt_comment').id, 
            #         partner_ids=partner_ids
            #     )
            # if self.user_id:
            #     model = self.env["ir.model"].sudo().search([("model", "=", "bi.purchase.order")])     
            #     data = {
            #         "res_id": self.id,
            #         "res_model_id": model.id,
            #         "user_id": self.user_id.id,
            #         "summary": _(('Your Material request has been approved')),
            #         "activity_type_id": self.env.ref("bi_purchase_requisition.material_request_approve_id").id
            #     }
            #     self.env["mail.activity"].sudo().create(data)


            # group_ids = [
            # self.env.ref('bi_purchase_requisition.purchase_rfq_user').id,]
            # user_list = self.env['res.users'].search([
            #                 ('groups_id', 'in', group_ids)
            #             ])
            # self.state = 'confirm'
   
    def action_cancel(self):
        for order in self:
            order.state = "cancel"

    def set_to_draft(self):
        self.revised_count += 1
        if self.revised_count == 1:
            self.old_name = self.name
            self.write(
                {'name': self.name + '-' + str(self.revised_count)})
        else:
            self.write(
                {'name': self.old_name + '-' + str(self.revised_count)})
        self.state = "draft"
        self.is_po_mail = False
        
     

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                seq_date = None
                if "date_order" in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals["date_order"]))
                seq_number = self.env["ir.sequence"].next_by_code("bi.purchase.order", sequence_date=seq_date) or "/"
                vals["name"] = seq_number

        res = super(BiPurchaseOrder, self).create(vals)      
        for user in res:    
            group_ids = [
                self.env.ref('bi_purchase_requisition.purchase_rfq_manager').id,
                self.env.ref('bi_purchase_requisition.purchase_rfq_user').id,

                ]
            user_list = self.env['res.users'].search([
                    ('groups_id', 'in', group_ids)
                ])
            partner_ids = user_list.mapped('partner_id').ids
            # if partner_ids:
            #     user.message_post(
            #         body=f"Purchase RFQ {user.name} has been created by {self.env.user.name}. "
            #             f"Please take the necessary actions to move forward.",
            #         subtype_id=self.env.ref('mail.mt_comment').id, 
            #         partner_ids=partner_ids
            #     )      
        return res
    
   


    def unlink(self):
        for order in self:
            if not order.state == "cancel":
                raise UserError(_("In order to delete a RFQ, you must cancel it first."))
        return super(BiPurchaseOrder, self).unlink()
    
    
    def get_purchase_quotation(self):
        return {
                "name": ("Purchase Quotation"),
                "res_model": "bi.purchase.quotation",
                # 'res_id':requisition_id.id,
                "view_mode": "list,form",
                "type": "ir.actions.act_window",
                "domain": [("bi_purchase_id", "=", self.id), ("state", "!=", "cancel")],
                # 'context': {'default_partner_id': self.vendor_id.id if self.vendor_id.id else False}
                }  
      
    def get_purchase_order(self):
        return {
                "name": ("Purchase Order"),
                "res_model": "purchase.order",
                "view_mode": "list,form",
                "type": "ir.actions.act_window",
                "domain": [("material_req_id", "=", self.id), ("state", "!=", "cancel")],
                }

    def select_line(self):
        product_list = []
        for each in self.order_line:
            if each.is_select and each.product_qty>0:
                product_list.append((0, 0, {
                            'product_id': each.product_id.id,
                            'name':each.name,
                            'product_uom':each.product_uom.id,
                            'product_qty': each.product_qty,
                            'price_unit':each.price_unit,
                            'taxes_id':each.taxes_id.ids,
                            'purchase_orderline_id':each.id
                            # 'price_subtotal': each.price_subtotal,
                        }))
        partner = []
        if self.vendor_id:
            for each in self.vendor_id:
                partner.append(each.id)
            

        return {
            'type': 'ir.actions.act_window',
            'name': _("Create requisition Wizard"),
            'view_mode': 'form',
            'res_model': 'quotation.wizard',
            'target': 'new',
            'context':{
                    'default_rfq_id':self.id,
                    'default_partner_domain_ids':partner,
                    'default_payment_term_id':self.payment_term_id.id,
                    # 'default_partner_ref' :  self.partner_ref,
                    'default_m_number':self.m_number,
                    'default_job_number':self.job_number.id,
                    'default_quotation_wiz_line_ids': product_list,
                    
                },
        }
        
    
class BiPurchaseOrderLine(models.Model):
    _name = "bi.purchase.order.line"
    _description = "BI Purchase Order Line"
    _inherit = ["mail.thread"]

    is_select = fields.Boolean(string="Select")
    order_id = fields.Many2one("bi.purchase.order", string="Purchase Order")
    sequence = fields.Integer(string="Sequence", default=10)
    name = fields.Text(string="Description", required=True)
    product_id = fields.Many2one(
        "product.product", string="Product", domain=[("purchase_ok", "=", True)], change_default=True
    )
    qty_done = fields.Float(string="Qty Done")
    product_qty = fields.Float(string="Quantity", digits="Product Unit of Measure", required=True)
    product_uom_qty = fields.Float(string="Total Quantity", compute="_compute_product_uom_qty", store=True)
    price_unit = fields.Float(string="Unit Price", digits="Product Price")
    discount = fields.Float(string="Discount (%)", digits="Discount", default=0.0)
    product_uom = fields.Many2one("uom.uom", string="Unit of Measure")
    # product_uom_category_id = fields.Many2one(related="product_id.uom_id.category_id")
    taxes_id = fields.Many2many("account.tax", string="Taxes", domain=[("type_tax_use", "=", "purchase")])
    # taxes_id = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Monetary(compute="_compute_price_subtotal", string="Subtotal", store=True)
    price_total = fields.Monetary(compute="_compute_price_subtotal", string="Total", store=True)
    # price_tax = fields.Float(compute="_compute_amount", string="Tax", store=True)
    currency_id = fields.Many2one(related="order_id.currency_id", store=True, string="Currency", readonly=True)
    display_type = fields.Selection(
        [("line_section", "Section"), ("line_note", "Note")], default=False, help="Technical field for UX purpose."
    )
    date_planned = fields.Datetime(string="Scheduled Date", index=True)
    state = fields.Selection(
        string="Status",
        related="order_id.state",
        readonly=True,
        index=True,
        copy=False,
        tracking=True,
        store=True,
    )
    is_uom_domain_ids = fields.Many2many("uom.uom", string="Uom Domain")


    @api.onchange("product_uom")
    def _onchange_product_uom(self):
        for rec in self:
            if rec.product_id and rec.product_id.uom_id:
                product_uom_category = rec.product_id.uom_id.category_id.id
                category = self.env['uom.category'].sudo().search([('id', '=', product_uom_category)], limit=1)
                if category:
                    # list_ids = category.uom_ids.ids
                    self.is_uom_domain_ids = category.uom_ids.ids
                    # return {"domain": {"product_uom": [("id", "in", category.uom_ids.ids)]}}

    
    @api.onchange('product_id')
    def _auto_loading_uom(self):
        if self.product_id:
            self.product_uom = self.product_id.uom_id.id
            self.price_unit = self.product_id.standard_price
        else:
            self.product_uom = False
            self.price_unit = False
            

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
    