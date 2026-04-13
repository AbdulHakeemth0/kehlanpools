from odoo import api, fields, models, Command, _


class AccountMove(models.Model):
    _inherit = 'account.payment'

    is_invoice_due = fields.Boolean(string="Is Invoice", default=False)
    sum_of_invoice = fields.Char(string="Sum of Invoice", tracking=True, compute='_compute_invoice_due_pay')
    inv_det = fields.Char(string="Invoice details",compute='_compute_invoice_due_pay')


    @api.depends('partner_id')
    def _compute_invoice_due_pay(self):
        for each in self:
            if each.partner_id:
                customer_invoice_ids = self.env['account.move'].search([('partner_id','=',each.partner_id.id),('move_type', '=', 'out_invoice'),('payment_state', '=', 'not_paid')])
                if customer_invoice_ids and each.payment_type == 'inbound':
                    each.is_invoice_due = True
                    sum_amt = 0
                    inv_val = ' '
                    for move in customer_invoice_ids:
                        if move.amount_residual != 0 and move.name:
                            inv_val += ', '+(move.name+'-'+str(move.amount_residual)+ self.env.user.currency_id.name)
                        sum_amt += move.amount_residual
                    each.sum_of_invoice = str(round(sum_amt,3)) + ' ' + self.env.user.currency_id.name
                    each.inv_det = inv_val
                else:
                    each.is_invoice_due = False
                    each.sum_of_invoice = ''
                    each.inv_det = ''
            else:
                each.is_invoice_due = False
                each.sum_of_invoice = ''
                each.inv_det = ''   
      
    """
        Override
        Error during payment, overrided to fix it.
    """
    def _generate_journal_entry(self, write_off_line_vals=None, force_balance=None, line_ids=None):
        need_move = self.filtered(lambda p: not p.move_id and p.outstanding_account_id)
        assert len(self) == 1 or (not write_off_line_vals and not force_balance and not line_ids)

        move_vals = []
        for pay in need_move:
            move_vals.append({
                'move_type': 'entry',
                'ref': pay.memo,
                'date': pay.date,
                'journal_id': pay.journal_id.id,
                'company_id': pay.company_id.id,
                'partner_id': pay.partner_id.id,
                'currency_id': pay.currency_id.id,
                'partner_bank_id': pay.partner_bank_id.id,
                'line_ids': line_ids or [
                    Command.create(line_vals)
                    for line_vals in pay._prepare_move_line_default_vals(
                        write_off_line_vals=write_off_line_vals,
                        force_balance=force_balance,
                    )
                ],
                'origin_payment_id': pay.id,
            })
        moves = self.env['account.move'].create(move_vals)
        if moves:
            for pay, move in zip(need_move, moves):
                pay.write({'move_id': move.id, 'state': 'in_process'})
            
