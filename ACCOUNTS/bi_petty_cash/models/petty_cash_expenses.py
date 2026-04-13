from odoo import fields, models, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from datetime import date


class PettyCashExpense(models.Model):
    _name = "petty.cash.expenses"
    _description = "Petty Cash Expenses"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"
    _rec_name = "number"

    @api.model
    def _default_payment_journal(self):
        company_id = self._context.get("company_id", self.env.user.company_id.id)
        domain = [
            ("type", "in", ("bank", "cash")),
            ("company_id", "=", company_id),
        ]
        return self.env["account.journal"].search(domain, limit=1)
    
    name = fields.Char("Payment Memo", default="", copy=False, tracking=True)
    date = fields.Date("Date", index=True, copy=False, default=fields.Date.context_today, tracking=True)
    account_date = fields.Date(
        "Accounting Date",
        index=True,
        help="Effective date for accounting entries",
        copy=False,
        default=fields.Date.context_today,
        tracking=True
    )
    journal_id = fields.Many2one(
        "account.journal",
        "Journal",
        required=True,
        domain="[('type', 'in', ['cash', 'bank'])]",
        tracking=True
    )
    payment_journal_id = fields.Many2one(
        "account.journal",
        string="Payment Method",
        domain="[('type', 'in', ['cash', 'bank'])]",
        default=_default_payment_journal,
    )
    account_id = fields.Many2one(
        "account.account",
        "Account",
        required=True,
        related="journal_id.default_account_id",
    )
    line_ids = fields.One2many("petty.cash.expenses.line", "voucher_id", "Voucher Lines", copy=True)
    narration = fields.Text("Notes")
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        store=True,
        default=lambda self: self.env.company.currency_id.id,
        tracking=True
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        store=True,
        related="journal_id.company_id",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            # ("create", "Business Head Approval"),
            ("request", "Request for Approval"),
            ("approve", "Approved"),
            ("cancel", "Cancelled"),
            ("reject", "Reject")
        ],
        "Status",
        tracking=True,
        copy=False,
        default="draft",
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated "
             "and voucher entries are created in account.\n"
             " * The 'Cancelled' status is used when user cancel voucher.",
    )
    reference = fields.Char("Reference", help="The partner reference of this document.", copy=False, tracking=True)
    amount = fields.Monetary(string="Total", store=True, compute="_compute_total")
    tax_amount = fields.Monetary(store=True, compute="_compute_total")
    tax_correction = fields.Monetary(help="In case we have a rounding problem in the tax, use this field to correct it")
    number = fields.Char(string="Number", copy=False, compute="_compute_number")
    petty_cash_number = fields.Char(string="Petty Cash Name")
    move_id = fields.Many2one("account.move", "Journal Entry", copy=False)
    partner_id = fields.Many2one("res.partner", "Partner", change_default=1)
    # paid = fields.Boolean(compute="_compute_check_paid", help="The Voucher has been totally paid.")
    document_date = fields.Date(
        string="Document Date",
        default=fields.Date.context_today,
        tracking=True
    )
    pay_now = fields.Selection(
        [
            ("pay_now", "Pay Directly"),
            ("pay_later", "Pay Later"),
        ],
        "Payment",
        index=True,
        default="pay_now",
    )
    date_due = fields.Date("Due Date", index=True)
    request_user_id = fields.Many2one(
        string="Request User ID",
        comodel_name="res.users",
        tracking=True
    )
    request_date = fields.Date(
        string="Request date",
    )
    approved_user_id = fields.Many2one(
        string="Approved User ID",
        comodel_name="res.users",
    )
    approved_date = fields.Date(
        string="Approved date",
    )
    reject_user_id = fields.Many2one(
        string="Rejected User ID",
        comodel_name="res.users",
    )
    reject_date = fields.Date(
        string="Rejected date",
    )
    begining_balance = fields.Float(string="Beginning Balance", readonly=True, tracking=True)
    add_allocation = fields.Float(string="Additional Allocation")
    cash_outward = fields.Float(string="Cash Outward", compute="_compute_opening_balance")
    closing_balance = fields.Float(
        string="Closing Balance", compute="_compute_opening_balance", tracking=True
    )
    date_month = fields.Char(compute="_compute_date_month", string="Month")
    employee_id = fields.Many2one("hr.employee", string="Custodian", required=True, tracking=True)
    attachment_ids = fields.Many2many("ir.attachment", string="Attachment", tracking=True)

    # is_business_head = fields.Boolean(compute='_compute_is_business_head')
    # is_account_manager = fields.Boolean(compute='_compute_is_account_manager')
    # is_audit_executive = fields.Boolean(compute='_compute_is_audit_executive')
    
    # sale_order_id = fields.Many2one(
    #     string='Sale Order',
    #     comodel_name='sale.order',
    #     ondelete='restrict',
    # )
    
    # ... To filter the so which have the division - CORPORATE EVENTS and DSW EVENTS ... #
    # @api.onchange("sale_order_id")
    # def _onchange_sale_order_id(self):
    #     division_ids = self.env['bi.department'].search([('code', 'in', ['0001','008'])])
    #     sale_order_ids= self.env['sale.order'].search(
    #         [('bi_department_id','in', division_ids.ids)
    #             ])
    #     domain = [("id", "in", sale_order_ids.ids)]
    #     return {"domain": {"sale_order_id": domain}}
    
    # def _compute_is_business_head(self):
    #     for rec in self:
    #         if self.env.user.user_has_groups('bi_petty_cash.group_business_head') and rec.state == 'create':
    #             rec.is_business_head = True
    #         else:
    #             rec.is_business_head = False
    #
    # def _compute_is_account_manager(self):
    #     for rec in self:
    #         if self.env.user.user_has_groups('account.group_account_user') and rec.state == 'request':
    #             rec.is_account_manager = True
    #         else:
    #             rec.is_account_manager = False
    #
    # def _compute_is_audit_executive(self):
    #     for rec in self:
    #         if self.env.user.user_has_groups(
    #                 'account.group_account_readonly') and rec.state == 'audit_executive_approval':
    #             rec.is_audit_executive = True
    #         else:
    #             rec.is_audit_executive = False

    def action_business_head_approval(self):
        if not self.line_ids:
            raise UserError(_("Bill information not entered!!!"))
        self.state = 'account_manager_approval'

    def proforma_voucher(self):
        pass
        # if self.amount <= 0:
        #     raise UserError(_("You cannot create petty cash expense with amount is zero"))
        # if not self.line_ids:
        #     raise UserError(_("Bill information not entered!!!"))
        # # self.state = 'audit_executive_approval'
        # self.write(
        #     {
        #         "state": "approve",
        #         "request_user_id": self.env.user.id,
        #         "request_date": date.today(),
        #     }
        # )

    @api.depends("tax_correction", "line_ids.price_subtotal")
    def _compute_total(self):
        tax_calculation_rounding_method = self.env.user.company_id.tax_calculation_rounding_method
        for voucher in self:
            total = 0
            tax_amount = 0
            tax_lines_vals_merged = {}
            for line in voucher.line_ids:
                tax_info = line.tax_ids.compute_all(
                    line.price_unit,
                    voucher.currency_id,
                    line.quantity,
                    line.product_id,
                    voucher.partner_id,
                )
                if tax_calculation_rounding_method == "round_globally":
                    total += tax_info.get("total_excluded", 0.0)
                    for t in tax_info.get("taxes", False):
                        key = (
                            t["id"],
                            t["account_id"],
                        )
                        if key not in tax_lines_vals_merged:
                            tax_lines_vals_merged[key] = t.get("amount", 0.0)
                        else:
                            tax_lines_vals_merged[key] += t.get("amount", 0.0)
                else:
                    total += tax_info.get("total_included", 0.0)
                    tax_amount += sum(t.get("amount", 0.0) for t in tax_info.get("taxes", False))
            if tax_calculation_rounding_method == "round_globally":
                tax_amount = sum(voucher.currency_id.round(t) for t in tax_lines_vals_merged.values())
                voucher.amount = total + tax_amount + voucher.tax_correction
            else:
                voucher.amount = total + voucher.tax_correction
            voucher.tax_amount = tax_amount

    @api.onchange("employee_id", "journal_id", "currency_id")
    def _onchange_employee_id(self):
        total_imburse_amount = total_alloc_amount = 0
        if self.employee_id:
            pettycash_imbursement_ids = self.env["petty.cash.imbursement"].search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("journal_id", "=", self.journal_id.id),
                    ("state", "=", "approve"),
                ]
            )
            for imbursement in pettycash_imbursement_ids:
                total_imburse_amount += imbursement.currency_id._convert(
                    imbursement.amount, self.currency_id, self.env.company, self.date
                )

            alloc_ids = self.env["petty.cash.expenses"].search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("journal_id", "=", self.journal_id.id),
                    ("state", "=", "approve"),
                ]
            )
            petty_exp_ids = alloc_ids.filtered(lambda x: x.cash_outward > 0)
            for alloc in petty_exp_ids:
                total_alloc_amount += alloc.currency_id._convert(
                    alloc.amount, self.currency_id, self.env.company, self.date
                )
                
            # petty_cash_transfer_ids = self.env["petty.cash.transfer"].search(
            #     [
            #         ("employee_id", "=", self.employee_id.id),
            #         ("journal_id", "=", self.journal_id.id),
            #         ("state", "=", "transfer"),
            #     ]
            # )
            # for transfer in petty_cash_transfer_ids:
            #     custodian_transfer += transfer.currency_id._convert(
            #         transfer.pending_amount, self.currency_id, self.env.company, self.date
            #     )

            # current_employee_transfer_ids = self.env["petty.cash.transfer"].search(
            #     [
            #         ("transfer_employee_id", "=", self.employee_id.id),
            #         ("journal_id", "=", self.journal_id.id),
            #         ("state", "=", "receive"),
            #     ]
            # )
            # for current_emp in current_employee_transfer_ids:
            #     current_employee += current_emp.currency_id._convert(
            #         current_emp.pending_amount, self.currency_id, self.env.company, self.date
            #     )

            # balance_amount = total_imburse_amount - total_alloc_amount - custodian_transfer + current_employee
            
            balance_amount = total_imburse_amount - total_alloc_amount
            self.write({"begining_balance": balance_amount})

    @api.constrains('line_ids')
    def _check_balance_amt(self):
        if self.begining_balance == 0:
            raise UserError(_("You cannot create petty cash expense with zero beginning balance"))

    @api.model_create_multi
    def create(self, vals_list):
        records = super(PettyCashExpense, self).create(vals_list)
        for record in records:
            if record.amount == 0:
                raise UserError(_("You cannot create petty cash expense with an amount of zero."))
        return records

    @api.depends("date")
    def _compute_date_month(self):
        for each in self:
            if each.date:
                each.date_month = each.date.strftime("%b")
            else:
                each.date_month = False

    # @api.depends("move_id.line_ids.reconciled", "move_id.line_ids.account_id.internal_type")
    # def _compute_check_paid(self):
    #     for record in self:
    #         record.paid = any(
    #             [
    #                 (line.account_id.internal_type in ("receivable", "payable") and line.reconciled)
    #                 for line in record.move_id.line_ids
    #             ]
    #         )
    @api.model
    def _get_currency(self):
        journal = self.env["account.journal"].browse(self.env.context.get("default_journal_id", False))
        if journal.currency_id:
            return journal.currency_id.id
        return self.env.user.company_id.currency_id.id

    @api.model
    def _get_company(self):
        return self._context.get("company_id", self.env.user.company_id.id)

    @api.constrains("company_id", "currency_id")
    def _check_company_id(self):
        for voucher in self:
            if not voucher.company_id:
                raise ValidationError(_("Missing Company"))
            if not voucher.currency_id:
                raise ValidationError(_("Missing Currency"))

    @api.depends("move_id")
    def _compute_number(self):
        for record in self:
            if record.move_id:
                record.number = record.move_id.name
                record.petty_cash_number = record.move_id.name
            else:
                record.number = "New"
                record.petty_cash_number = "New"

    @api.onchange("date")
    def onchange_date(self):
        self.account_date = self.date

    def action_cancel_draft(self):
        self.write({"state": "draft"})

    def button_create(self):
        if self.amount <= 0:
            raise UserError(_("You cannot create petty cash expense with amount is zero"))
        if not self.line_ids:
            raise UserError(_("Bill information not entered!!!"))
        # self.state = 'audit_executive_approval'
        users = self.env.ref('bi_petty_cash.group_petty_cash').users
        model = self.env["ir.model"].sudo().search([("model", "=", "petty.cash.expenses")],limit=1)     
        for each_user in users:
            usr_id = each_user  
            data = {
                "res_id": self.id,
                "res_model_id": model.id,
                "user_id": usr_id.id,
                "summary": _(('A petty cash expense request has been sent by-%s') % (
                                str( self.env.user.name))),
                "activity_type_id": self.env.ref("bi_petty_cash.petty_cash_activity_id").id
            }
            self.env["mail.activity"].sudo().create(data)
        self.write({"state": "request"})

    def cancel_voucher(self):
        for voucher in self:
            voucher.move_id.button_cancel()
            voucher.move_id.unlink()
        self.write({"state": "draft", "move_id": False})

    def unlink(self):
        for voucher in self:
            if voucher.state not in ("draft", "cancel"):
                raise UserError(_("Cannot delete voucher(s) which are already opened or paid."))
            if voucher.state == "approve":
                raise UserError(_("You cannot delete this Record."))
        return super(PettyCashExpense, self).unlink()

    # <<<<....This 'Business head approval' is removed, said by dsw team 'jan/25/24'....>>>>
    def action_request(self):
        # Check amount zero or not
        if self.amount <= 0:
            raise UserError(_("You cannot create petty cash expense with amount is zero"))
    #     # Check if another entry exist for the custodian
    #     # expenses_id = self.env["petty.cash.expenses"].search(
    #     #     [("employee_id", "=", self.employee_id.id),
    #     #      ("state", "=", "request")]
    #     # )
    #     # if len(expenses_id) > 0:
    #     #     raise UserError(_("Another entry exists for the Custodian"))
    #     self.write(
    #         {
    #             "state": "request",
    #             "request_user_id": self.env.user.id,
    #             "request_date": date.today(),
    #         }
    #     )

    def button_reject(self):
        self.write(
            {
                "state": "reject",
                "reject_user_id": self.env.user.id,
                "reject_date": date.today(),
            }
        )

    def action_account_manager_approval(self):
        if not self.line_ids:
            raise UserError(_("Bill information not entered!!!"))
        if self.begining_balance == 0:
                raise UserError(_("No balance !!"))
        model = self.env["ir.model"].sudo().search([("model", "=", "petty.cash.expenses")],limit=1) 
        for order in self:
            user_id = order.employee_id.user_id.id
            if user_id:
                data = {
                    "res_id": order.id,
                    "res_model_id": model.id,
                    "user_id": user_id,
                    "summary": _(('Petty cah request has been approved by the manager')),
                    "activity_type_id": self.env.ref("bi_petty_cash.petty_cash_activity_id").id
                }
                self.env["mail.activity"].sudo().create(data)
            list_val = []
            amount = 0.0
            tax_credit = 0.0
            company_currency = self.env.company.currency_id
            current_currency = self.currency_id
            if order.currency_id.id == self.env.company.currency_id.id:
                for line in order.line_ids:
                    if not line.tax_ids:
                        amount += line.price_unit
                        debit = line.price_unit
                    else:
                        amount += line.price_subtotal
                        debit = line.price_subtotal
                    list_val.append(
                        (
                            0,
                            0,
                            {
                                "account_id": line.account_id.id,
                                "name": line.name,
                                "partner_id": line.res_partner_petty_cash_id.id,
                                "debit": debit,
                                # "analytic_account_id": line.account_analytic_id.id if line.account_analytic_id else False,
                                # "analytic_tag_ids": [(6, 0, line.analytic_tag_ids.ids)],
                                "credit": 0.0,
                            },
                        )
                    )
                list_val.append(
                    (
                        0,
                        0,
                        {
                            "account_id": order.account_id.id,
                            "name": line.name,
                            "debit": 0.0,
                            "credit": self.amount,
                            # "analytic_account_id": line.account_analytic_id.id if line.account_analytic_id else False,
                            # "analytic_tag_ids": [(6, 0, line.analytic_tag_ids.ids)],
                        },
                    )
                )
                if order.line_ids.tax_ids:
                    list_val.append(
                        (
                            0,
                            0,
                            {
                                "account_id": order.line_ids.tax_ids[0].invoice_repartition_line_ids.account_id.id,
                                "name": line.name,
                                "debit": self.tax_amount,
                                "credit": 0.0,
                                # "analytic_account_id": line.account_analytic_id.id if line.account_analytic_id else False,
                                # "analytic_tag_ids": [(6, 0, line.analytic_tag_ids.ids)],
                            },
                        )
                    )
                values = {
                    "date": order.document_date,
                    "company_id": order.company_id.id,
                    "ref": order.reference,
                    "journal_id": order.journal_id.id,
                    "move_type": "entry",
                    "line_ids": list_val,
                }
            else:
                for line in order.line_ids:
                    rate = order.currency_id.compute(line.price_unit, self.env.company.currency_id)
                    # Need to correct to exact convert compute function
                    amount += rate
                    list_val.append(
                        (
                            0,
                            0,
                            {
                                "account_id": line.account_id.id,
                                "partner_id": line.res_partner_petty_cash_id.id,
                                "debit": rate,
                                # "analytic_account_id": line.account_analytic_id.id if line.account_analytic_id else False,
                                # "analytic_tag_ids": [(6, 0, line.analytic_tag_ids.ids)],
                                "credit": 0.0,
                                # "currency_id": company_currency != current_currency and current_currency.id or False,
                                # "amount_currency": company_currency != current_currency and order.amount or 0.0,
                            },
                        )
                    )
                list_val.append(
                    (
                        0,
                        0,
                        {
                            "account_id": order.account_id.id,
                            "debit": 0.0,
                            "credit": amount,
                            # "analytic_account_id": line.account_analytic_id.id if line.account_analytic_id else False,
                            # "analytic_tag_ids": [(6, 0, line.analytic_tag_ids.ids)],
                            # "currency_id": company_currency != current_currency and current_currency.id or False,
                            # "amount_currency": company_currency != current_currency and -1.0 * order.amount or 0.0,
                        },
                    )
                )
                values = {
                    "date": order.document_date,
                    "journal_id": order.journal_id.id,
                    "move_type": "entry",
                    "company_id": order.company_id.id,
                    "line_ids": list_val,
                }
            account_move_id = self.env["account.move"].sudo().create(values)
            account_move_id.action_post()
            if account_move_id:
                order.write(
                    {
                        "move_id": account_move_id.id,
                        "state": "approve",
                        "approved_user_id": self.env.user.id,
                        "approved_date": date.today(),
                    }
                )

    @api.depends("begining_balance", "amount")
    def _compute_opening_balance(self):
        for order in self:
            cash_outward = 0
            closing_balance = 0
            if not order.employee_id:
                begining_balance = 0
            else:
                begining_balance = order.begining_balance
            if begining_balance:
                closing_balance = begining_balance - order.amount
            if closing_balance < 0 and order.amount:
                raise UserError(_("No balance !!"))
            cash_outward = begining_balance - closing_balance
            order.write(
                {"closing_balance": closing_balance, "begining_balance": begining_balance, "cash_outward": cash_outward}
            )


class PettyCashExpensesLine(models.Model):
    _name = "petty.cash.expenses.line"
    _description = "Petty Cash Expenses Line"

    name = fields.Text(string="Description", required=True)
    sequence = fields.Integer(
        default=10, help="Gives the sequence of this line when displaying the voucher.", copy=False
    )
    voucher_id = fields.Many2one("petty.cash.expenses", string="Voucher", ondelete="cascade")
    product_id = fields.Many2one("product.product", string="Product", ondelete="set null", index=True)
    job_no = fields.Many2one('sale.order',string="Job Number", domain="[('type', 'in', ['vas'])]")
    account_id = fields.Many2one(
        "account.account",
        string="Account",
        required=True,
        domain=[("deprecated", "=", False)],
        help="The income or expense account related to the selected product.",
    )
    price_unit = fields.Float(
        string="Unit Price",
        required=True,
        digits="Product Price"
    )
    price_subtotal = fields.Monetary(string="Subtotal", store=True, compute="_compute_subtotal")
    quantity = fields.Float(digits="Product Unit of Measure", required=True, default=1)
    # account_analytic_id = fields.Many2one("account.analytic.account", "Analytic Account")
    # analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")
    company_id = fields.Many2one("res.company", related="voucher_id.company_id", string="Company", store=True)
    tax_ids = fields.Many2many("account.tax", string="Tax", help="Only for tax excluded from price")
    currency_id = fields.Many2one("res.currency", related="voucher_id.currency_id", readonly=False)

    res_partner_petty_cash_id = fields.Many2one("res.partner", string="Partner")
    # account_analytic_ids = fields.Many2many(
    #     "account.analytic.account",
    #     string="Analytic Accounts",
    # )
    # sale_order_id = fields.Many2one(
    #     string='Sale Order',
    #     comodel_name='sale.order',
    #     ondelete='restrict',
    # )
    
    @api.onchange("tax_ids")
    def _onchange_tax_ids(self):
        purchase_tax_ids = self.env['account.tax'].search(
            [
                ('type_tax_use', '=', 'purchase'), 
                ])
        domain = [("id", "in", purchase_tax_ids.ids)]
        return {"domain": {"tax_ids": domain}}


    @api.depends("price_unit", "tax_ids", "quantity", "product_id", "voucher_id.currency_id")
    def _compute_subtotal(self):
        for rec in self:
            rec.price_subtotal = rec.quantity * rec.price_unit
            if rec.tax_ids:
                taxes = rec.tax_ids.compute_all(
                    rec.price_unit,
                    rec.voucher_id.currency_id,
                    rec.quantity,
                    product=rec.product_id,
                    partner=rec.voucher_id.partner_id,
                )
                rec.price_subtotal = taxes["total_excluded"]

    # @api.depends("account_analytic_id")
    # def _compute_account_analytic_id(self):
    #     for line in self:
    #         account_analytic_ids = self.env["account.analytic.account"].search(
    #             [("group_id.is_employee_group", "=", True)]
    #         )
    #         line.account_analytic_ids = [(6, 0, account_analytic_ids.ids)]
