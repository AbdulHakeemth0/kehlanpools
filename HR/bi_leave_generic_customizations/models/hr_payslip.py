from odoo import models, fields, api,_
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class HrPayslip(models.Model):
    _inherit = "hr.payslip"


    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'COO'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Canceled')],
        string='Status', index=True, readonly=True, copy=False,
        default='draft', tracking=True,
        help="""* When the payslip is created the status is \'Draft\'
                \n* If the payslip is under verification, the status is \'Waiting\'.
                \n* If the payslip is confirmed then status is set to \'Done\'.
                \n* When the user cancels a payslip, the status is \'Canceled\'.""")

    def compute_sheet(self):
        res = super().compute_sheet()
        for rec in self:
            model = self.env["ir.model"].sudo().search([("model", "=", "hr.payslip")],limit=1)
            users = self.env.ref('bi_leave_generic_customizations.group_ceo_related').users
            for user in users:
                data = {
                    "res_id": rec.id,
                    "res_model_id": model.id,
                    "user_id": user.id,
                    "summary": f'{rec.employee_id.name} payslip has been created {self.env.user.name}',
                    "activity_type_id": self.env.ref("bi_leave_generic_customizations.payslip_create_activity_id").id
                }
                self.env["mail.activity"].sudo().create(data)
        return res 

    def action_payslip_done(self):
        res = super().action_payslip_done()
        for each in self:
            model = self.env["ir.model"].sudo().search([("model", "=", "hr.payslip")],limit=1)
            users = self.env.ref('bi_leave_generic_customizations.group_accounts_related').users
            for user in users:
                data = {
                    "res_id": each.id,
                    "res_model_id": model.id,
                    "user_id": user.id,
                    "summary": f'{each.employee_id.name} payslip has been Approved by {self.env.user.name}',
                    "activity_type_id": self.env.ref("bi_leave_generic_customizations.payslip_create_activity_id").id
                }
                self.env["mail.activity"].sudo().create(data)
        return res

    @api.depends('employee_id', 'contract_id', 'struct_id', 'date_from', 'date_to')          
    def _compute_input_line_ids(self):
        """ Compute Maternity Leave Salary and Pass it to Payslip Inputs """
        res = super()._compute_input_line_ids()
        for rec in self:
            if rec.employee_id and rec.struct_id:
                maternity_leave_type = rec.env['hr.leave.type'].search([('is_maternity_leave', '=', True)], limit=1)
                paternity_leave_type = rec.env['hr.leave.type'].search([('is_paternity_leave', '=', True)], limit=1)
                marriage_leave_type = rec.env['hr.leave.type'].search([('is_marriage_leave', '=', True)], limit=1)
                if maternity_leave_type:
                    maternity_leaves = rec.env['hr.leave'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('holiday_status_id', '=', maternity_leave_type.id),
                        ('state', '=', 'validate'),
                        ('request_date_from', '>=', rec.date_from),
                        ('request_date_to', '<=', rec.date_to)
                    ])
                    maternity_input_type = rec.env['hr.payslip.input.type'].search([('code', '=', "MATERNITY")], limit=1)
                    if maternity_leaves:
                        if not maternity_input_type:
                            continue
                        existing_rule = rec.struct_id.rule_ids.filtered(lambda x: x.code == "MATERNITY_PAY")
                        if existing_rule:
                            existing_line = rec.input_line_ids.filtered(lambda line: line.input_type_id == maternity_input_type)

                            if existing_line:
                                existing_line.write({
                                    'amount': 0,
                                    'name': "Maternity Leave Payment"
                                })
                            else:
                                to_add_vals = {
                                    'amount': 0,
                                    'input_type_id': maternity_input_type.id,
                                    'name': "Maternity Leave Payment"
                                }
                                rec.update({'input_line_ids': [(0, 0, to_add_vals)]})
                    else:
                        rec.input_line_ids = [(2, line.id) for line in rec.input_line_ids if line.input_type_id == maternity_input_type]

                if paternity_leave_type:
                    paternity_leaves = rec.env['hr.leave'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('holiday_status_id', '=', paternity_leave_type.id),
                        ('state', '=', 'validate'),
                        ('request_date_from', '>=', rec.date_from),
                        ('request_date_to', '<=', rec.date_to)
                    ])
                    paternity_input_type = rec.env['hr.payslip.input.type'].search([('code', '=', "PATERNITY")], limit=1)
                    if paternity_leaves:
                        if not paternity_input_type:
                            continue
                        existing_rule = rec.struct_id.rule_ids.filtered(lambda x: x.code == "PATERNITY_PAY")
                        if existing_rule:
                            existing_line = rec.input_line_ids.filtered(lambda line: line.input_type_id == paternity_input_type)

                            if existing_line:
                                existing_line.write({
                                    'amount': 0,
                                    'name': "Paternity Leave Payment"
                                })
                            else:
                                to_add_vals = {
                                    'amount': 0,
                                    'input_type_id': paternity_input_type.id,
                                    'name': "Paternity Leave Payment"
                                }
                                rec.update({'input_line_ids': [(0, 0, to_add_vals)]})
                    else:
                        rec.input_line_ids = [(2, line.id) for line in rec.input_line_ids if line.input_type_id == paternity_input_type]

                if marriage_leave_type:
                    marriage_leaves = rec.env['hr.leave'].search([
                        ('employee_id', '=', rec.employee_id.id),
                        ('holiday_status_id', '=', marriage_leave_type.id),
                        ('state', '=', 'validate'),
                        ('request_date_from', '>=', rec.date_from),
                        ('request_date_to', '<=', rec.date_to)
                    ])

                    marriage_input_type = rec.env['hr.payslip.input.type'].search([('code', '=', "MARRIAGE")], limit=1)
                    existing_line = rec.input_line_ids.filtered(lambda line: line.input_type_id == marriage_input_type)
                    if not marriage_input_type:
                        continue
                    if marriage_leaves:
                        existing_rule = rec.struct_id.rule_ids.filtered(lambda x: x.code == "MARRIAGE_PAY")
                        if existing_rule:
                            if existing_line:
                                existing_line.write({
                                    'amount': 0,
                                    'name': "Marriage Leave Payment"
                                })
                            else:
                                to_add_vals = {
                                    'amount': 0,
                                    'input_type_id': marriage_input_type.id,
                                    'name': "Marriage Leave Payment"
                                }
                                rec.update({'input_line_ids': [(0, 0, to_add_vals)]})
                    else:
                        rec.input_line_ids = [(2, line.id) for line in rec.input_line_ids if line.input_type_id == marriage_input_type]

        return res
    

    # when this function override the remove 'The employee bank account is untrusted' this user error
    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.payment.register wizard.
        '''
        if any(state == 'paid' for state in self.mapped('state')):
            raise UserError(_("You can only register payments for unpaid documents."))
        if not self.struct_id.rule_ids.filtered(lambda r: r.code == "NET").account_credit.reconcile:
            raise UserError(_('The credit account on the NET salary rule is not reconciliable'))
        bank_account = self.employee_id.sudo().bank_account_id
        if bank_account and not bank_account.allow_out_payment: #change in this line
            raise UserError(_('The employee bank account is untrusted'))
        if any(m.state != 'posted' for m in self.move_id):
            raise UserError(_("You can only register payment for posted journal entries."))
        return self.move_id.line_ids.action_register_payment(
            ctx={"default_partner_id": self.employee_id.work_contact_id.id,
                 "default_partner_bank_id": bank_account.id})
