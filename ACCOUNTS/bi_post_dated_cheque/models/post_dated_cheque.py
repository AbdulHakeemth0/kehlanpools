from datetime import date

from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class PostDatedCheque(models.Model):
    _name = 'post.dated.cheque'
    _description = 'Post Dated Cheque'
    _rec_name = 'bank_acc_id'

    bank_id = fields.Many2one('res.bank', string="Bank")
    
    bank_acc_id = fields.Many2one(
        'account.journal',
        string="Bank ", 
        required=True,
        domain="[('type', '=', 'bank')]",
        )
    no_of_cheques = fields.Integer(string='Number of Cheques', required=True)
    partner_id = fields.Many2one('res.partner', string="Supplier")
    customer_id = fields.Many2one('res.partner', string="Customer")
    starting_cheque_number = fields.Char(string='Starting Cheque Number', required=True)
    starting_cheque_date = fields.Date(string='Starting Cheque Date')
    cheque_line_ids = fields.One2many('post.dated.cheque.line', 'cheque_id', string='Cheque Lines')
    cheques_generated = fields.Boolean(string='Cheques Generated', default=False, readonly=True)
    payment_generated = fields.Boolean(string='Payment Generated', default=False, readonly=True)
    payment_type = fields.Selection([
        ('send', 'Send'),
        ('receive', 'Receive'),
    ], string='Type', default='send', required=True, tracking=True)
    cheque_type = fields.Selection([
        ('cdc', 'CDC'),
        ('pdc', 'PDC'),
    ], string='Cheque Type', default='cdc', required=True, tracking=True)
    cheque_payment_type = fields.Selection([
        ('month', 'Monthly'),
        ('quartely', 'Quartely'),
    ], string='Payment', default='month', required=True)
    amount = fields.Float(string="Cheque Amount")
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("cheques_generated", "Cheques Generated"),
            ("payment_created", "Payment Created"),
        ],
        string="State",
        default="draft",
        required=True,
        copy=False,
    )
    
    def generate_cheques(self):
        if self.no_of_cheques and self.starting_cheque_number:
            cheque_lines = []
            cheque_number_length = len(self.starting_cheque_number)
            start_number_int = int(self.starting_cheque_number)
            start_date = self.starting_cheque_date or date.today()
            for i in range(self.no_of_cheques):
                if self.cheque_payment_type == 'month':
                   date_vaue = start_date + relativedelta(months=i)
                if self.cheque_payment_type == 'quartely':
                    date_vaue = start_date + relativedelta(months=i*3)
                current_cheque_number = str(start_number_int + i).zfill(cheque_number_length)
                cheque_lines.append((0, 0, {
                    'cheque_id': self.id,
                    'cheque_number': current_cheque_number,
                    'cheque_date': date_vaue,
                    'cheque_amount': self.amount,
                    'remarks': '',
                })) 
            self.cheque_line_ids = cheque_lines
            self.cheques_generated = True
            self.state = 'cheques_generated'
        else:
            raise UserError("Please provide both the number of cheques and the starting cheque number.")
    
    def create_payment(self):
        for rec in self:
            if rec.payment_type == 'send' and rec.cheque_type == 'pdc':
                for cheque_line in self.cheque_line_ids:
                    pdc_vals = {
                        'partner_id': self.partner_id.id,
                        'check_number': cheque_line.cheque_number,
                        'check_date': cheque_line.cheque_date,
                        'check_amount': cheque_line.cheque_amount,
                        'pdc_type': 'vendor',
                        'bank_journal_id': self.bank_acc_id.id,
                        'account_new_id': self.bank_acc_id.id,   
                        'state': 'draft',
                    }

                    pdc_record = self.env['post.dated.check'].create(pdc_vals)
                    if not pdc_record:
                        raise UserError(_("Failed to create Post Dated Cheque record."))
                    pdc_record.action_pdc_send_receive()
                    pdc_record.action_pdc_deposit()
                    rec.payment_generated = True
                    rec.state = 'payment_created'
                    
            if rec.payment_type == 'receive' and rec.cheque_type == 'pdc':
                for cheque_line in self.cheque_line_ids:
                    pdc_vals = {
                        'partner_id': self.customer_id.id,
                        'check_number': cheque_line.cheque_number,
                        'check_date': cheque_line.cheque_date,
                        'check_amount': cheque_line.cheque_amount,
                        'pdc_type': 'customer',
                        'bank_journal_id': self.bank_acc_id.id,
                        'account_new_id': self.bank_acc_id.id,   
                        'state': 'draft',
                    }

                    pdc_record = self.env['post.dated.check'].create(pdc_vals)
                    if not pdc_record:
                        raise UserError(_("Failed to create Post Dated Cheque record."))
                    rec.payment_generated = True
                    rec.state = 'payment_created'
                    
            if rec.payment_type == 'send' and rec.cheque_type == 'cdc':
                for line in rec.cheque_line_ids:
                    cdc_payment = {
                        'partner_id': rec.partner_id.id,
                        'payment_type': 'outbound',  
                        'partner_type': 'supplier',
                        'journal_id': rec.bank_acc_id.id,
                        'amount': line.cheque_amount,
                        'date': line.cheque_date,
                    }

                    payment = self.env['account.payment'].create(cdc_payment)
                    if not payment:
                        raise UserError(_("Failed to create Current Dated Cheque payment."))
                    rec.payment_generated = True
                    rec.state = 'payment_created'
                    
            if rec.payment_type == 'receive' and rec.cheque_type == 'cdc':
                for line in rec.cheque_line_ids:
                    cdc_payment = {
                        'partner_id': rec.customer_id.id,
                        'payment_type': 'outbound',  
                        'partner_type': 'customer',
                        'journal_id': rec.bank_acc_id.id,
                        'amount': line.cheque_amount,
                        'date': line.cheque_date,
                    }

                    payment = self.env['account.payment'].create(cdc_payment)
                    if not payment:
                        raise UserError(_("Failed to create Current Dated Cheque payment."))
                    rec.payment_generated = True
                    rec.state = 'payment_created'
                
        
    def _valid_field_parameter(self, field, name):
        # Allow 'tracking' parameter for fields
        if name == 'tracking':
            return True
        return super()._valid_field_parameter(field, name)

class PostDatedChequeLine(models.Model):
    _name = 'post.dated.cheque.line'
    _description = 'Post Dated Cheque Line'

    cheque_id = fields.Many2one('post.dated.cheque', string='Post Dated Cheque', ondelete='cascade')
    cheque_number = fields.Char(string='Cheque Number', required=True)
    cheque_date = fields.Date(string='Cheque Date')
    cheque_amount = fields.Float(string='Cheque Amount', store=True)
    remarks = fields.Text(string='Remarks')
