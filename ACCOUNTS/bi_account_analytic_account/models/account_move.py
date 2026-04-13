from odoo import api, fields, models,_
from datetime import date
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    type = fields.Selection([
        ('vas', 'VAS'),
        ('amc', 'AMC'),
    ], string="Type(VAS/AMC)")

    job_no = fields.Char(
        string='Job No',
    )
    
    m_number = fields.Char(string="M-number")
    invoicing_percentage = fields.Float(string="Invoicing Percentage",tracking=True)
    acc_type = fields.Selection([
        ('BANK', 'BANK'),
        ('CASH', 'CASH'),
        ('JOURNAL','JOURNAL'),
    ], string="Account Type")
    
    lpo_no = fields.Char(
        string='LPO No',
    )
    sequence_no = fields.Char('Sequence No.',copy=False, default=lambda self: _('New'))
    adv_amount_received = fields.Float(
        string='Advance Amount Received',
    )

    def _valid_field_parameter(self, field, name):
        # EXTENDS models
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        current_date = date.today()
        current_year = current_date.year
        year = str(current_year)[2:]
        vas_journal = self.env['account.journal'].sudo().search([('amc_vas_type','=','vas')])
        amc_journal = self.env['account.journal'].sudo().search([('amc_vas_type','=','amc')])
        for vals in res:
            if vals.type:
                if vals.type == 'amc':
                    sequence = self.env['ir.sequence'].next_by_code('account.move.seq') or _("New")
                    vals.sequence_no = 'SA' +year+ sequence
                    vals.journal_id = amc_journal.id
                elif vals.type == 'vas':
                    sequence = self.env['ir.sequence'].next_by_code('account.move.vas') or _("New")
                    vals.sequence_no = 'SV' + year + sequence
                    vals.journal_id = vas_journal.id
        return res
    

    @api.onchange('type')
    def _onchange_type_amc_vas(self):
        vas_journal = self.env['account.journal'].sudo().search([('amc_vas_type','=','vas')])
        amc_journal = self.env['account.journal'].sudo().search([('amc_vas_type','=','amc')])
        if self.type == 'amc' and amc_journal:
            self.journal_id = amc_journal.id
        if self.type == 'vas' and vas_journal:
            self.journal_id = vas_journal.id
    delivery_note = fields.Char(string='Delivery Note')
    quotation_ref = fields.Char(string='Quotation Ref')
    terms_of_pay = fields.Char(string='Mode/Terms of Payment')
    other_ref = fields.Char(string='Other Reference(s)')
    buyers_order_no = fields.Char(string="Buyer's Order No")
    desp_through = fields.Char(string="Despatched through")
    dest = fields.Char(string="Destination")
    terms_of_del = fields.Char(string="Terms of Delivery")
    
    def update_invoice_numbers(self):
        so_ids = self.env['sale.order'].sudo().search([])
        for so in so_ids.order_line:
            invoices = self.env['account.move.line'].search([('sale_line_ids', '=', so.id)])
            for invoice in invoices:
                if so.order_id.m_number and not invoice.move_id.m_number:
                     invoice.move_id.write({'m_number': so.order_id.m_number})

    @api.onchange('invoicing_percentage')
    def _onchange_invoicing_percentage(self):
        for each in self:
            if each.invoicing_percentage:
                self.percentage_invoiced_amount = (each.amount_total*each.invoicing_percentage)/100
                if each.line_ids:
                    for each_line in each.line_ids:
                        each_line.invoice_percentage = each.invoicing_percentage
                        each_line.price_unit = each_line.price_unit * (each.invoicing_percentage)/100

    def update_analytic_account(self):
        AccountMoveLine = self.env['account.move.line']
        AnalyticAccount = self.env['account.analytic.account']
        Project = self.env['project.project']
        amc_analytic_account = AnalyticAccount.search([('is_amc', '=', True)], limit=1)
        vas_analytic_account = AnalyticAccount.search([('is_vas', '=', True)], limit=1)
        if not amc_analytic_account and not vas_analytic_account:
            return
        all_lines = AccountMoveLine.sudo().search([('move_id.move_type', 'in', ['out_invoice', 'out_refund'])])
        for line in all_lines:
            line.analytic_distribution = False  
            order_id = line.sale_line_ids.mapped('order_id')
            project = Project.search([('order_id', '=', order_id.id)], limit=1)
            analytic_account_id = project.account_id if project else False
            distribution = {}
            if analytic_account_id:
                distribution[str(analytic_account_id.id)] = 100
            if line.move_id.type == 'amc' and amc_analytic_account:
                distribution[str(amc_analytic_account.id)] = 100
            elif line.move_id.type == 'vas' and vas_analytic_account:
                distribution[str(vas_analytic_account.id)] = 100
            if distribution:
                line.analytic_distribution = distribution
            for deferred_line in line.move_id.deferred_move_ids.line_ids:
                deferred_move = deferred_line.move_id.deferred_original_move_ids
                order_id = deferred_move.line_ids.sale_line_ids.mapped('order_id')
                project = Project.search([('order_id', '=', order_id.id)], limit=1)
                analytic_account_id = project.account_id if project else False
                distribution = {}
                if analytic_account_id:
                    distribution[str(analytic_account_id.id)] = 100

                if deferred_move.type == 'amc' and amc_analytic_account:
                    distribution[str(amc_analytic_account.id)] = 100
                elif deferred_move.type == 'vas' and vas_analytic_account:
                    distribution[str(vas_analytic_account.id)] = 100

                if distribution:
                    deferred_line.analytic_distribution = distribution

        move_lines = AccountMoveLine.sudo().search([('move_id.move_type', 'in', ['entry']),('analytic_distribution','=',False),('name','ilike','Deferral of')])
        for line in move_lines:
            if not line.analytic_distribution and 'Deferral' in (line.name or ''):
                text = line.name
                parts = text.split(' ')
                if len(parts) >= 3:
                    ref = parts[-1]  
                move_id = self.env['account.move'].search([('name','=',ref)],limit=1)
                distribution = {}
                if move_id:
                    if move_id.type == 'amc' and amc_analytic_account:
                        distribution[str(amc_analytic_account.id)] = 100
                    elif move_id.type == 'vas' and vas_analytic_account:
                        distribution[str(vas_analytic_account.id)] = 100
                    if distribution:
                            line.analytic_distribution = distribution
                else:
                    if amc_analytic_account:
                        distribution[str(amc_analytic_account.id)] = 100
                    if distribution:
                            line.analytic_distribution = distribution


    def action_update_analytic_account_name(self):
        excluded_account_codes = ['251000', '10020201']
        for move in self:
            for line in move.line_ids:
                # Skip accounts that shouldn't have analytic distributions
                if line.account_id.code in excluded_account_codes:
                    line.analytic_distribution = False
                    continue
                distribution = line.analytic_distribution
                if distribution:
                    new_distribution = {}
                    updated = False
                    for acc_id, percent in distribution.items():
                        # Normalize 50% splits to 100%
                        if percent == 50:
                            new_distribution[acc_id] = 100
                            updated = True
                        else:
                            new_distribution[acc_id] = percent
                    if updated:
                        line.analytic_distribution = new_distribution
                        