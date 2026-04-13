from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError, ValidationError
from datetime import date


class RequestForAdvance(models.Model):
    _name = "request.advance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Request For Advance"
    _rec_name = "name"

    name = fields.Char(
        string="Name",
        default=lambda self: _("New"),
    )
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    department_id = fields.Many2one("hr.department", string="Department")
    approved_amount = fields.Float(string="Approve Amount")
    requested_amount = fields.Float(string="Requested Amount")
    approved_date = fields.Date(string="Approved Date")
    requested_date = fields.Date(string="Requested Date")
    job_position_id = fields.Many2one("hr.job", string="Job Position")
    currency_id = fields.Many2one("res.currency", string="Currency")
    is_deduct_from_salary = fields.Boolean(string="Deducted From Salary")
    entry_id = fields.Many2one('account.move',string="Entry")
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        default=lambda self: self.env.company
        
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("verify", "Verified"),
            ("approved", "Approved"),
            ('closed',"Closed"),
            ("refuse", "Refused"),
        ],
        string="Status",
        index=True,
        default="draft",
        store=True,
        tracking=True,
    )
    credit_account_id = fields.Many2one('account.account',string="Credit Account")
    debit_account_id = fields.Many2one('account.account',string="Debit Account")
    journal_id = fields.Many2one('account.journal',string="Journal",default=lambda self:self.env['account.journal'].search([('is_miscellaneous','=',True)]))

    def action_verify(self):
        if self.requested_amount <= 0:
            raise ValidationError(_("Please enter a valid requested amount."))
        self.write({"state": "verify"})
                

    def action_approve(self):
        amount = self.approved_amount
        lists = []
        if amount <= 0:
            raise ValidationError(_("Please enter a valid approve amount."))
        if not self.employee_id.contract_id.analytic_account_id:
             raise UserError(_("The employee contract has no analytic account specified."))
        lists.append(
                (
                    0,
                    0,
                    {
                        "account_id": self.debit_account_id.id,
                        "debit": amount,
                        "credit": 0.0,
                        "analytic_distribution":({self.employee_id.contract_id.analytic_account_id.id: 100}),
                        "name": "Advance Salary of "+str(self.employee_id.name),
                    },
                )
            )
        lists.append(
                (
                    0,
                    0,
                    {
                        "account_id": self.credit_account_id.id,
                        "debit": 0.0,
                        "credit": amount,
                        "name": "Advance Salary of "+str(self.employee_id.name),
                    
                    },
                )
            )
        values = {
                "date": self.requested_date,
                "journal_id": self.journal_id.id,
                "move_type": "entry",
                "ref": "Advance Salary",
                "line_ids": lists,
            }
        account_move_id = self.env["account.move"].sudo().create(values)
        account_move_id.action_post()
        if account_move_id:
            self.write({"state": "approved"})
            self.entry_id = account_move_id.id
        self.approved_date = date.today()
            
    def action_refuse(self):
        self.write({"state": "refuse"})

    def action_set_to_draft(self):
        self.write({"state": "draft"})

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("request.advance.seq")
        return super().create(vals_list)

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        for rec in self:
            rec.department_id = rec.employee_id.department_id.id
            rec.job_position_id = rec.employee_id.job_id.id