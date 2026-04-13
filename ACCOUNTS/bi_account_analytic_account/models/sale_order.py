from odoo import api, fields, models,_
from odoo.exceptions import UserError, ValidationError
from datetime import date
from datetime import datetime,timedelta
import calendar
from dateutil.relativedelta import relativedelta





class SaleOrder(models.Model):
    _inherit ='sale.order'

    def _prepare_invoice(self):
        """Super sale order class and update with fields"""
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'type': self.type,
        })
        return invoice_vals

    def _create_invoices(self, grouped=False, final=False, date=None):
        for each in self:
            moves = super()._create_invoices(grouped=grouped, final=final, date=date)
            project_id = self.env['project.project'].search([('order_id', '=', self.id)])
            analytic_account_id = project_id.account_id
            vas_journal = self.env['account.journal'].sudo().search([('amc_vas_type','=','vas')])
            amc_journal = self.env['account.journal'].sudo().search([('amc_vas_type','=','amc')])
            if self.next_invoice_date:
                current_datetime = self.next_invoice_date
            else:
                current_datetime = datetime.now()    
            current_year = current_datetime.year
            year = str(current_year)[2:]
            for move in moves:
                if each.type:
                    move.type = each.type
                    if move.type == 'vas':
                        sequence = self.env['ir.sequence'].next_by_code('account.move.vas') or _("New")
                        move.sequence_no = 'SV' + year + sequence
                        if vas_journal:
                            move.journal_id = vas_journal.id
                        else:
                            raise ValidationError(_("Please provide VAS journal..."))
                    if move.type == 'amc':
                        sequence = self.env['ir.sequence'].next_by_code('account.move.seq') or _("New")
                        move.sequence_no = 'SA' + year + sequence        
                        if amc_journal:
                            move.journal_id = amc_journal.id
                        else:
                            raise ValidationError(_("Please provide AMC journal..."))
                        
                        for line in move.invoice_line_ids:
                            start_date = current_datetime
                            start_date_new = start_date.strftime("%d/%m/%Y")
                            date_start =  datetime.strptime(start_date_new, '%d/%m/%Y')
                            last_day = False
                            end_date = False
                            if line.sale_line_ids.order_id.plan_id.is_weekly:
                                last_day = date_start + timedelta(days=7)

                            if line.sale_line_ids.order_id.plan_id.is_monthly:
                                last_day = date_start + relativedelta(months=1) - timedelta(days=1)

                            if line.sale_line_ids.order_id.plan_id.is_quaterly:
                                last_day = date_start + relativedelta(months=3) - timedelta(days=1)

                            if line.sale_line_ids.order_id.plan_id.is_bi_yearly:
                                last_day = date_start + relativedelta(months=6) - timedelta(days=1)

                            if line.sale_line_ids.order_id.plan_id.is_yearly:
                                last_day = date_start + relativedelta(years=1) - timedelta(days=1)
                         
                            if last_day:
                                end_date = last_day.strftime("%d/%m/%Y")
                            label = start_date_new + ' to ' + end_date
                            line.product_label = label
                            line.write({'product_label': line.product_label})

                    if each.m_number:
                        move.m_number = each.m_number
                for line in move.invoice_line_ids:
                    if each.type == 'amc':
                        amc_analytic_account = self.env['account.analytic.account'].search([('is_amc', '=', True)],limit=1)
                        line.analytic_distribution =  {str(analytic_account_id.id): 100, str(amc_analytic_account.id):100}
                    if each.type == 'vas':
                        vas_analytic_account = self.env['account.analytic.account'].search([('is_vas', '=', True)],limit=1)
                        line.analytic_distribution =  {str(analytic_account_id.id): 100, str(vas_analytic_account.id):100}
                for line in move.line_ids:
                    if each.type == 'amc':
                        line.analytic_distribution = False
                        amc_analytic_account = self.env['account.analytic.account'].search([('is_amc', '=', True)], limit=1)
                        distribution = {}
                        if analytic_account_id:
                            distribution[str(analytic_account_id.id)] = 100
                        if amc_analytic_account:
                            distribution[str(amc_analytic_account.id)] = 100
                        line.write({'analytic_distribution': distribution})
                        # total = sum(distribution.values())
                        # if total > 0:
                        #     normalized = {k: round(v * 100.0 / total, 2) for k, v in distribution.items()}
                        #     line.write({'analytic_distribution': normalized})
                    if each.type == 'vas':
                        line.analytic_distribution = False
                        amc_analytic_account = self.env['account.analytic.account'].search([('is_vas', '=', True)], limit=1)
                        distribution = {}
                        if analytic_account_id:
                            distribution[str(analytic_account_id.id)] = 100
                        if amc_analytic_account:
                            distribution[str(amc_analytic_account.id)] = 100
                        line.write({'analytic_distribution': distribution})
                        # total = sum(distribution.values())
                        # if total > 0:
                        #     normalized = {k: round(v * 100.0 / total, 2) for k, v in distribution.items()}
                        #     line.write({'analytic_distribution': normalized})
            return moves