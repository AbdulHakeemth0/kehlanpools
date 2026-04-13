from dateutil.relativedelta import relativedelta
from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    civil_warranty = fields.Float(string="Civil Warranty")
    civil_warranty_period = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Civil Warranty Period", tracking=True)
    warranty_expire_date = fields.Date(string="Warranty Expiry Date")
    invoice_percentage = fields.Float(string="INV %")

    @api.model
    def _get_warranty_expiry_date(self):
        for line in self:
            if line.civil_warranty and line.civil_warranty_period and line.move_id.invoice_date:
                warranty_duration = line.civil_warranty
                invoice_date = line.move_id.invoice_date
                if line.civil_warranty_period == 'days':
                    line.warranty_expire_date = invoice_date + relativedelta(days=warranty_duration)
                elif line.civil_warranty_period == 'months':
                    line.warranty_expire_date = invoice_date + relativedelta(months=warranty_duration)
                elif line.civil_warranty_period == 'years':
                    line.warranty_expire_date = invoice_date + relativedelta(years=warranty_duration)

class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(AccountMove, self).action_post()
        for line in self.invoice_line_ids:
            line._get_warranty_expiry_date()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'invoice_line_ids' in vals:
                for line_vals in vals['invoice_line_ids']:
                    if isinstance(line_vals, (list, tuple)) and line_vals[0] == 0:  # Check for new records
                        product_id = line_vals[2].get('product_id')
                        if product_id:
                            product = self.env['product.product'].browse(product_id)
                            if product.warranty_type == 'civil':
                                line_vals[2]['civil_warranty'] = product.civil_warranty
                                line_vals[2]['civil_warranty_period'] = product.civil_warranty_period

        return super(AccountMove, self).create(vals_list)