from odoo import models, fields, api, _
from odoo.exceptions import UserError 

class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "Purchase Request"
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    PURCHASE_REQUEST_STATES = [
    ('draft', 'Draft'),
    ('approve', 'Approved'),
    ('in_progress', 'Requisition'),
    # ('done', 'Closed'),
    ('cancel', 'Rejected')
]
    
    @api.depends('purchase_request_ids.price_subtotal')
    def _compute_amount_total(self):
        for order in self:
            amount = 0.0
            for line in order.purchase_request_ids:
                amount += line.price_subtotal
            order.update({
                'amount_total': amount,
            })
    

    
    
    name = fields.Char(string="PR Number", default="New", copy=False)
    user_id = fields.Many2one(
        "res.users",
        string="Initiated By",
        index=True,
        tracking=True,
        default=lambda self: self.env.user,
    )
    partner_ref = fields.Char('Subject', copy=False,required = True,
                              help="Reference of the sales order or bid sent by the vendor. "
                              "It's used to do the matching when you receive the "
                              "products as this reference is usually written on the "
                              "delivery order sent by your vendor.")
    
    m_number = fields.Char(string="M-number")
    job_number = fields.Many2one("sale.order", string="Job number", domain="[('type', '=', 'vas')]")
    
    state = fields.Selection(PURCHASE_REQUEST_STATES,
                              'Status', tracking=True, required=True,
                              copy=False, default='draft')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_amount_total')
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.company.currency_id.id)
    date_order = fields.Datetime('PR Date', required=True, index=True, copy=False, default=fields.Datetime.now,
                                help="Depicts the date where the Quotation should be validated and converted into a purchase order.") 
    date_end = fields.Datetime(string='Expected Order', tracking=True)
    
    reason_for_reject = fields.Char(string = "Rejected Reason")
    is_rejected = fields.Boolean(string = "Is Rejected")
    
    
    purchase_request_ids = fields.One2many('purchase.request.line', 'requisition_id', string='Product Details', copy=True)
    
    requisition_id = fields.Many2one('purchase.requisition.new', string='Requisition')

    
    
    
    
    def confirm(self):
        for rec in self:
            if self.purchase_request_ids:
                rec.state = 'approve'
                for user in rec:
                    group_ids = [
                        self.env.ref('bi_purchase_requisition.purchase_rfq_user').id,

                    ]
                user_list = self.env['res.users'].search([
                        ('groups_id', 'in', group_ids)
                    ])
                partner_ids = user_list.mapped('partner_id').ids
                # if partner_ids:
                #     user.message_post(
                #         body=f"Initial purchase request {user.name} has been approved by {self.env.user.name}. "
                #             f"Please take the necessary actions to create Purchase Requisition.",
                #         subtype_id=self.env.ref('mail.mt_comment').id, 
                #         partner_ids=partner_ids
                #     )

            else:
               raise UserError(_("Provide Product details to confirm Purchase Request")) 
           
           
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                seq_date = None
                if "date_order" in vals:
                    seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals["date_order"]))
                seq_number = self.env["ir.sequence"].next_by_code("purchase.request", sequence_date=seq_date) or "/"
                vals["name"] = seq_number
            res = super(PurchaseRequest, self).create(vals_list)      
            for user in res:    
                if user.user_id.id:
                    employee = self.env['hr.employee'].sudo().search([('user_id', '=', user.user_id.id)])
                    # if employee.parent_id:
                    #     user.message_post(
                    #         body=f"Initial purchase request {user.name} has been created by {user.user_id.name}."
                    #             f"Please take the necessary actions to move forward.",
                    #         subtype_id=self.env.ref('mail.mt_comment').id, 
                    #         partner_ids=employee.parent_id.user_partner_id.ids
                    #     )        
    
        return res
    
    def cancel(self):
        for rec in self:
            # rec.state = 'cancel'
            
            return {
                    "type": "ir.actions.act_window",
                    "view_mode": "form",
                    "res_model": "reject.wizard",
                    "views": [(False, "form")],
                    "view_id": False,
                     "target": "new",
                    "context": {
                                "default_initial_purchase_request_id": self.id, 
                            }
                }   

        
    def create_purchase_requisition(self):
        line_list = []
        for rec in self.purchase_request_ids:
            line_list.append(
                (
                    0,
                    0,
                    {
                        "name": rec.name,
                        "product_qty": rec.product_qty,
                        "price_unit": rec.price_unit,
                        "price_subtotal": rec.price_subtotal,
                        # "currency_id": rec.currency_id,

                    },
                )
            )
            
            values = {
                "partner_ref": self.partner_ref,
                "pr_approved_line": line_list,
                "date_order":self.date_order,
                "date_end":self.date_end,
            }
        requisition = self.env['purchase.requisition.new'].create(values)
        # requisition.button_submit()
        self.requisition_id = requisition
        self.state = 'in_progress'
        
    # def approve(self):
    #     for rec in self:
    #         rec.state = 'approve'       
    def get_requisition(self):
        return {
            "name": ("Purchase Requisition"),
            "res_model": "purchase.requisition.new",
            # 'res_id':requisition_id.id,
            "view_mode": "list,form",
            "type": "ir.actions.act_window",
            "domain": [("id", "=", self.requisition_id.id), ("state", "!=", "cancel")],
            # 'context': {'default_partner_id': self.vendor_id.id if self.vendor_id.id else False}
        }
        
    @api.model
    def search_fetch(self, domain=None, field_names=None, offset=0, limit=None, order=None):
        # if domain is None:
        #     domain = [('user_id', '=', self.env.user.id)]
        # user_employee = self.env.user.employee_id    
        # if not self.env.user.has_group('bi_purchase_requisition.purchase_request_access_manager'):
        #     domain += [('user_id', '=', self.env.user.id)]   
        # else:    
        #     subordinate_ids = self.env['hr.employee'].search([
        #         ('parent_id', '=', user_employee.id)
        #         ]).mapped('user_id.id')
        #     subordinate_ids.append(user_employee.user_id.id)
        #     domain += [('user_id', 'in', subordinate_ids)] 
        return super(PurchaseRequest, self).search_fetch(domain, field_names, offset, limit, order)
    



    def bulk_create_purchase_requisition(self):
        
        line_list = []
        for requests in self:
            if requests.state == 'draft':
                raise UserError(_("Initial Purchase Request Not Approved Yet!"))
            if requests.state == 'in_progress':
                raise UserError(_("Purchase Requisition already created for %s")%(requests.name))
            for rec in requests.purchase_request_ids:
                line_list.append(
                    (
                        0,
                        0,
                        {
                            "name": rec.name,
                            "product_qty": rec.product_qty,
                            "price_unit": rec.price_unit,
                            "price_subtotal": rec.price_subtotal,
                            # "currency_id": rec.currency_id,

                        },
                    )
                )
            
        values = {
            # "partner_ref": 'test',
            "pr_approved_line": line_list,
            "date_order":fields.Datetime.today(),
            # "date_end":self.date_end,
        }
        requisition = self.env['purchase.requisition.new'].create(values)
        requisition.button_submit()
        for requests in self:
            requests.requisition_id = requisition
            requests.state = 'in_progress'

    def select_line(self):
        product_list = []
        for each in self.purchase_request_ids:
            if each.is_select:
                product_list.append((0, 0, {
                            'name': each.name,
                            'product_qty': each.product_qty,
                            'price_unit':each.price_unit,
                            'price_subtotal': each.price_subtotal,
                        }))
        return {
            'type': 'ir.actions.act_window',
            'name': _("Create request Wizard"),
            'view_mode': 'form',
            'res_model': 'purchase.request.wizard',
            'target': 'new',
            'context':{
                    'default_request_id':self.id,
                    'default_partner_ref' :  self.partner_ref,
                    'default_date_order': self.date_order,
                    'default_date_end': self.date_end,
                    'default_m_number':self.m_number,
                    'default_job_number':self.job_number.id,
                    'default_requisition_wiz_line_ids': product_list,
                    
                },
        }
      




    # def bulk_create_purchase_requisition(self):
    #     for requests in self:
    #         line_list = []
    #         for rec in requests.purchase_request_ids:
    #             line_list.append(
    #                 (
    #                     0,
    #                     0,
    #                     {
    #                         "name": rec.name,
    #                         "product_qty": rec.product_qty,
    #                         "price_unit": rec.price_unit,
    #                         "price_subtotal": rec.price_subtotal,
    #                         # "currency_id": rec.currency_id,

    #                     },
    #                 )
    #             )
            
    #     values = {
    #         "partner_ref": self.partner_ref,
    #         "pr_approved_line": line_list,
    #         "date_order":self.date_order,
    #         "date_end":self.date_end,
    #     }
    #     requisition = self.env['purchase.requisition.new'].create(values)
    #     requisition.button_submit()
    #     self.requisition_id = requisition
    #     self.state = 'in_progress'
    
    
class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Purchase Request Line"  
    
    requisition_id = fields.Many2one('purchase.request',string = "Purchase Request")
    is_select = fields.Boolean(string="Select")
    name = fields.Char(string = "Description") 
    reason_to_buy = fields.Char(string = "Reason to buy")
    product_qty = fields.Float(string = "Quantity")
    price_unit = fields.Float(string = "Unit Price")
    price_subtotal = fields.Monetary(string = "Subtotal", compute='_compute_price_subtotal', store=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
                                  default=lambda self: self.env.company.currency_id.id)
    
    
    @api.depends('product_qty', 'price_unit')
    def _compute_price_subtotal(self):
        for line in self:
            line.update({
                'price_subtotal': line.product_qty * line.price_unit,
            })
     
