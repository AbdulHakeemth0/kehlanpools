from odoo import _, fields, models, api
from odoo.exceptions import UserError
from datetime import datetime

class AccountStatementWizard(models.TransientModel):
    _name = "account.statement.wizard"
    _description = "account statement wizard"

    def _get_company(self):
        return (
            self.env["res.company"].browse(self.env.context.get("force_company"))
            or self.env.user.company_id
        )

    partner_id = fields.Many2one(
        "res.partner",
    )
    date_start = fields.Date('Date start', default=datetime.today())
    date_end = fields.Date('Date End', default=datetime.today())
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=_get_company,
        string="Company",
        required=True,
    )
    show_aging_buckets = fields.Boolean(default=True)
    filter_partners_non_due = fields.Boolean(
        string="Don't show partners with no due entries", default=True
    )
    filter_negative_balances = fields.Boolean("Exclude Negative Balances", default=True)
    aging_type = fields.Selection(
        [("days", "Age by Days"), ("months", "Age by Months")],
        string="Aging Method",
        default="days",
        required=True,
    )
    account_type = fields.Selection(
        [("asset_receivable", "Receivable"), ("payable", "Payable")],
        string="Account type",
        default="asset_receivable",
    )
    

    def _prepare_statement(self):
        self.ensure_one()
        partner_lst = list(set(vals.partner_id.id for vals in self))
        invoices = self.env['account.move'].search([
            ('partner_id', 'in', partner_lst),
            ('move_type', 'in', ['out_invoice', 'out_refund','entry']),
            ('state', '=', 'posted')
        ])
        payments = self.env['account.payment'].search([
            ('partner_id', 'in', partner_lst),
            ('state', '=', 'posted')
        ])
        # bank_ids
        partner = self.env['res.partner'].search([('id','in',partner_lst)])
        
        banks = self.env['account.account'].search([
            ('id', '=', partner.property_account_receivable_id.id)
        ]).code

        return {
            "date_start" :self.date_start,
            "date_end": self.date_end,
            "company_id": self.company_id.id,
            "partner_ids": partner_lst,
            "show_aging_buckets": self.show_aging_buckets,
            "filter_non_due_partners": self.filter_partners_non_due,
            "account_type": self.account_type if self.env.context.get('is_customer') else 'liability_payable',
            "aging_type": self.aging_type,
            # "filter_negative_balances": self.filter_negative_balances,
            "filter_negative_balances": False,
            "is_outstanding": True,
            "invoices": invoices,
            "payments": payments,
            "banks": banks,
        }

    def print_pdf(self):
        data = self._prepare_statement()
        if not self.partner_id:
            raise UserError(_("Please select a customer."))
        return self.env.ref(
            "bi_partner_statement_of_account.action_report_account_followup_new"
            # "bi_partner_statement_of_account.action_print_outstanding_statement"
        ).report_action(self.partner_id.id, data=data)
            
    def print_followup_report_xlsx(self, context=None):
        if not self.partner_id:
            raise UserError(_("Please select a customer."))
        # context = self._context
        # datas = {"ids": context.get("active_id", [])}
        # datas["partner_id"] = self.partner_id.id
        # datas["form"] = self.read()[0]
        data = self._prepare_statement()
        # report = self.env["ir.actions.report"]._get_report_from_name(
        #     "bi_partner_statement_of_account.account_followup_report_excel_new"
        # )
        # report.sudo().report_file = str("Account Followup Excel Report")
        return self.env.ref("bi_partner_statement_of_account.action_report_account_statement_xlsx").report_action(
            self.ids, data=data, config=False
        )
