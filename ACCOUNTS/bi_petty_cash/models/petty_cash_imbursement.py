from odoo import fields, models, api, _
from datetime import date
from odoo.exceptions import UserError


class PettyCashImbursement(models.Model):
    _name = "petty.cash.imbursement"
    _description = "Petty Cash imbursement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"
    _rec_name = "number"


    @api.model
    def get_account_domain(self):
        domain = []
        domain.append(("account_type", "=", "asset_cash"))
        return domain

    name = fields.Char("Payment Memo", copy=False, tracking=True)
    partner_id = fields.Many2one(
        "res.partner",
        "Partner",
        change_default=1,
        tracking=True
    )
    employee_id = fields.Many2one("hr.employee", string="Custodian", tracking=True, required=True)
    account_id = fields.Many2one("account.account", "Account", required=True, domain=get_account_domain, tracking=True)
    reference = fields.Char("Reference", help="The partner reference of this document.", copy=False, tracking=True)
    journal_id = fields.Many2one(
        "account.journal",
        "Journal",
        required=True,
        domain="[('is_petty_cash', '=', True),('company_id','=',company_id)]",
        tracking=True
    )
    date = fields.Date("Date", index=True, copy=False, default=fields.Date.context_today, tracking=True)
    account_date = fields.Date(
        "Accounting Date",
        readonly=True,
        index=True,
        help="Effective date for accounting entries",
        copy=False,
        default=fields.Date.context_today,
    )
    date_due = fields.Date(
        "Due Date",
        readonly=True,
        index=True,
        tracking=True
    )
    account_account_id = fields.Many2one("account.account", "Acc", required=True, tracking=True)
    description = fields.Char(string="Description")
    amount = fields.Monetary(string="Amount", tracking=True)
    narration = fields.Text("Notes", readonly=True, )
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
        readonly=True,
        default=lambda self: self._get_company(),
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("request", "Request For Approval"),
            ("approve", "Approved"),
            ("reject", "Rejected"),
            ("cancel", "Cancelled"),
            ("posted", "Posted"),
        ],
        "Status",
        readonly=True,
        tracking=True,
        copy=False,
        default="draft",
        help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Voucher.\n"
             " * The 'Pro-forma' status is used when the voucher does not have a voucher number.\n"
             " * The 'Posted' status is used when user create voucher,a voucher number is generated "
             "and voucher entries are created in account.\n"
             " * The 'Cancelled' status is used when user cancel voucher.",
    )

    move_id = fields.Many2one("account.move", "Journal Entry", copy=False)
    # account_analytic_id = fields.Many2one("account.analytic.account", "Analytic Account")
    # analytic_tag_ids = fields.Many2many("account.analytic.tag", string="Analytic Tags")
    number = fields.Char(copy=False, default=lambda self: _("New"))
    request_user_id = fields.Many2one(
        string="Request User ID",
        comodel_name="res.users",
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
    document_date = fields.Date(
        string="Document Date",
        default=fields.Date.context_today,
    )
    rejected_user_id = fields.Many2one(
        string="Rejected User ID",
        comodel_name="res.users",
    )
    rejected_date = fields.Date(
        string="Rejected date",
    )

    # is_account_manager = fields.Boolean(compute='_compute_is_account_manager')
    # is_audit_executive = fields.Boolean(compute='_compute_is_audit_executive')

    # def _compute_is_account_manager(self):
    #     for rec in self:
    #         if self.env.user.user_has_groups('account.group_account_user') and rec.state == 'verify':
    #             rec.is_account_manager = True
    #         else:
    #             rec.is_account_manager = False
    #
    # def _compute_is_audit_executive(self):
    #     for rec in self:
    #         if self.env.user.user_has_groups('account.group_account_readonly') and rec.state == 'approve':
    #             rec.is_audit_executive = True
    #         else:
    #             rec.is_audit_executive = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            res = super(PettyCashImbursement, self).create(vals)
            if res.amount <= 0:
                raise UserError(_("You cannot create petty cash imbursement with amount is zero"))
            return res

    def write(self, vals):
        res = super(PettyCashImbursement, self).write(vals)
        if vals.get("amount") == 0:
            raise UserError(_("You cannot create petty cash expense with amount is zero"))
        return res

    @api.onchange("journal_id")
    def onchange_journal_id(self):
        for order in self:
            order.account_account_id = order.journal_id.default_account_id.id
            company_id = self._context.get("company_id", self.env.user.company_id.id)
            domain = [
                ("type", "=", "cash"),
                ("company_id", "=", company_id),
            ]
            journal_ids = self.env["account.journal"].search(domain)
            return {"domain": {"journal_id": [("id", "in", journal_ids.ids)]}}

    @api.model
    def _get_currency(self):
        journal = self.env["account.journal"].browse(self.env.context.get("default_journal_id", False))
        if journal.currency_id:
            return journal.currency_id.id
        return self.env.user.company_id.currency_id.id

    @api.model
    def _get_company(self):
        return self._context.get("company_id", self.env.user.company_id.id)

    def action_request(self):
        sequence = self.env["ir.sequence"].with_company(self.company_id.id).next_by_code("code.imbursement")
        self.write(
            {"state": "request", "request_user_id": self.env.user.id, "request_date": date.today(), "number": sequence}
        )
        user_list = []
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('bi_petty_cash.group_petty_cash'):
                user_list.append(user.id)
        for each_user in user_list:
            usr_id = each_user
            model = self.env["ir.model"].sudo().search([("model", "=", "petty.cash.imbursement")])     
            data = {
                "res_id": self.id,
                "res_model_id": model.id,
                "user_id": usr_id,
                "summary": _(('A petty cash request has been sent by-%s') % (
                                str(self.request_user_id.name))),
                "activity_type_id": self.env.ref("bi_petty_cash.petty_cash_activity_id").id
            }
            self.env["mail.activity"].sudo().create(data)
        

    # Function to run scheduler to pass petty cash number to account lines
    def action_pass_description(self):
        for order in self:
            if order.move_id:
                for line in order.move_id.line_ids:
                    line.name = order.number

    def button_approve(self):
        for order in self:
            user_id = order.employee_id.user_id.id
            if user_id:
                model = self.env["ir.model"].sudo().search([("model", "=", "petty.cash.imbursement")]) 
                data = {
                    "res_id": self.id,
                    "res_model_id": model.id,
                    "user_id": user_id,
                    "summary": _(('Petty cah request has been approved by the manager')),
                    "activity_type_id": self.env.ref("bi_petty_cash.petty_cash_activity_id").id
                }
                self.env["mail.activity"].sudo().create(data)
            company_currency = self.env.company.currency_id
            current_currency = self.currency_id
            amount = current_currency._convert(order.amount, company_currency, order.env.company, order.date)
            lists = []
            lists.append(
                (
                    0,
                    0,
                    {
                        "account_id": order.account_id.id,
                        "debit": 0.0,
                        "credit": amount,
                        "name": order.number,
                        # "analytic_account_id": order.account_analytic_id.id if line.account_analytic_id else False,
                        # "analytic_tag_ids": [(6, 0, order.analytic_tag_ids.ids)],
                        # "currency_id": company_currency != current_currency and current_currency.id or False,
                        # "amount_currency": company_currency != current_currency and -1.0 * order.amount or 0.0,
                    },
                )
            )
            lists.append(
                (
                    0,
                    0,
                    {
                        "account_id": order.account_account_id.id,
                        "debit": amount,
                        "credit": 0.0,
                        "name": order.number,
                        # "analytic_account_id": order.account_analytic_id.id if line.account_analytic_id else False,
                        # "analytic_tag_ids": [(6, 0, order.analytic_tag_ids.ids)],
                        # "currency_id": company_currency != current_currency and current_currency.id or False,
                        # "amount_currency": company_currency != current_currency and order.amount or 0.0,
                    },
                )
            )
            values = {
                "date": order.document_date,
                "journal_id": order.journal_id.id,
                "move_type": "entry",
                "ref": order.reference,
                "company_id": order.company_id.id,
                "line_ids": lists,
            }
            account_move_id = self.env["account.move"].sudo().create(values)
            account_move_id.action_post()
            order.write(
                {
                    "move_id": account_move_id.id,
                    "approved_user_id": self.env.user.id,
                    "approved_date": date.today(),
                    "state": "approve"
                }
            )

    def button_cancel_entry(self):
        for rec in self:
            rec.move_id.button_cancel()
            rec.write({"state": "cancel"})

    def unlink(self):
        for imbursement in self:
            if imbursement.state == "approve":
                raise UserError(_("You cannot delete this Record."))
        return super(PettyCashImbursement, self).unlink()

    def show_transfer(self):
        for order in self:
            petty_cash_expenses_ids = self.env["petty.cash.expenses"].search([("employee_id", "=", order.employee_id.id)], order="document_date desc").ids
            return {
                "name": "Petty Cash Transfer",
                "type": "ir.actions.act_window",
                "view_mode": "list,form",
                "res_model": "petty.cash.expenses",
                "domain": [("id", "in", petty_cash_expenses_ids)],
                "target": "current",
            }

    def button_verify(self):
        self.write({"state": "verify"})


    def button_reject(self):
        self.write({"state": "reject", "rejected_user_id": self.env.user.id, "rejected_date": date.today()})
