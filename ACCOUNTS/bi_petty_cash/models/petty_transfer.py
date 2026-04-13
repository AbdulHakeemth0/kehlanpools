from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PettyCashTransfer(models.Model):
    _name = "petty.cash.transfer"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Petty Cash Transfer"
    _order = "date desc, id desc"
    _rec_name = "number"

    @api.model
    def get_journal_domain(self):
        domain = []
        domain.append(("type", "=", "cash"))
        return domain

    @api.model
    def _get_company(self):
        return self._context.get("company_id", self.env.user.company_id.id)

    number = fields.Char(copy=False, default=lambda self: _("New"))
    employee_id = fields.Many2one(
        "hr.employee",
        string="Custodian",
        required=True,
        tracking=True
    )
    transfer_employee_id = fields.Many2one("hr.employee", string="Transfer To", required=True, tracking=True)
    reference = fields.Char("Reference", help="The partner reference of this document.", copy=False, tracking=True)
    date = fields.Date("Date", index=True, copy=False, default=fields.Date.context_today, tracking=True)
    pending_amount = fields.Monetary(string="Pending Amount")
    journal_id = fields.Many2one("account.journal", "Journal", domain=get_journal_domain, tracking=True)
    account_id = fields.Many2one(
        "account.account",
        "Account",
        related="journal_id.default_account_id",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("create", "Created"),
            ("verify", "Verified"),
            (
                "approve",
                "Approved",
            ),
            ("transfer", "Transferred"),
            ("receive", "Received"),
            ("cancel", "Cancelled"),
        ],
        "Status",
        tracking=True,
        copy=False,
        default="draft",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        store=True,
        readonly=True,
        default=lambda self: self._get_company(),
    )

    @api.onchange("employee_id", "journal_id", "currency_id")
    def _onchange_employee_id(self):
        total_imburse_amount = total_alloc_amount = 0
        if self.employee_id:
            imbursement_ids = self.env["petty.cash.imbursement"].search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("journal_id", "=", self.journal_id.id),
                    ("state", "=", "posted"),
                ]
            )
            for imburstment in imbursement_ids:
                total_imburse_amount += imburstment.currency_id._convert(
                    imburstment.amount, self.currency_id, self.env.company, self.date
                )

            petty_cash_expense_ids = self.env["petty.cash.expenses"].search(
                [
                    ("employee_id", "=", self.employee_id.id),
                    ("journal_id", "=", self.journal_id.id),
                    ("state", "=", "posted"),
                ]
            )
            for exp in petty_cash_expense_ids:
                total_alloc_amount += exp.currency_id._convert(
                    exp.amount, self.currency_id, self.env.company, self.date
                )

            balance_amount = total_imburse_amount - total_alloc_amount
            self.write({"pending_amount": balance_amount})

    def action_to_create(self):
        if self.pending_amount == 0:
            raise UserError(_("You cannot create petty cash transfer with amount is zero"))
        sequence = self.env["ir.sequence"].next_by_code("code.transfer")
        self.write({"state": "create", "number": sequence})

    def action_to_transfer(self):
        self.write({"state": "transfer"})

    def cancel_voucher(self):
        self.write({"state": "cancel"})

    def unlink(self):
        for petty_cash in self:
            if petty_cash.state == "transfer":
                raise UserError(_("You cannot delete this Record."))
        return super(PettyCashTransfer, self).unlink()

    def button_verify(self):
        self.write({"state": "verify"})

    def button_receive(self):
        self.write({"state": "receive"})

    def button_approve(self):
        self.write({"state": "approve"})
