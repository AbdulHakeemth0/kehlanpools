from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    plan_end_date = fields.Date(compute='_compute_plan_end_date', string="Plan End Date")

    def _compute_plan_end_date(self):
        for order in self:
            plan = order.plan_id
            start_date = order.contract_start_date
            if start_date and plan:
                if plan.is_quaterly:
                    end_date = start_date + relativedelta(months=3)
                elif plan.is_monthly:
                    end_date = start_date + relativedelta(months=1)
                elif plan.is_yearly:
                    end_date = start_date + relativedelta(years=1)
                elif plan.is_bi_yearly:
                    end_date = start_date + relativedelta(months=6)
                else:
                    end_date = start_date

                # Subtract one day
                if end_date:
                    end_date_minus_one_day = end_date + relativedelta(days=-1)
                    order.plan_end_date = end_date_minus_one_day
                    date_start = start_date.strftime("%d/%m/%Y")
                    date_end = end_date_minus_one_day.strftime("%d/%m/%Y")
                    for line in order.order_line:
                        if not line.product_label:
                            line.product_label = f"{date_start} to {date_end}"
                else:
                    order.plan_end_date = False
            else:
                order.plan_end_date = False  # Or some default value
                


                
                
class SaleOrder(models.Model):
    _inherit = 'sale.order.line'


    product_label = fields.Char(string="Descriptions")
    
    def _prepare_invoice_line(self, **optional_values):
        invoice_line = super()._prepare_invoice_line(**optional_values)
        invoice_line['product_label'] = self.product_label
        # invoice_line['discount_amount'] = self.discount_amount
        return invoice_line
