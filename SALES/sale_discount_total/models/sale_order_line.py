from odoo import fields, models,api


class SaleOrderLine(models.Model):
    """This class inherits "sale.order.line" and adds fields discount,
     total_discount """
    _inherit = "sale.order.line"

    discount = fields.Float(string='Discount (%)', digits=(16, 20), default=0.0,
                            help="Discount needed.")
    total_discount = fields.Float(string="Total Discount", default=0.0,
                                  store=True, help="Total discount can be"
                                                   "specified here.")
    
    discount_amount = fields.Monetary(string="Discount Amount", store=True)

    @api.onchange('product_uom_qty','price_unit','discount_amount','product_id')
    def _onchange_discount_percentage(self):
        """
        Updates the discount amount when the discount percentage changes.
        """
        for line in self:
            if line.order_id.type == 'amc':
                amc_analytic_account = self.env['account.analytic.account'].search([('is_amc', '=', True)],limit=1)
                line.analytic_distribution = {str(amc_analytic_account.id): 100}
            if line.order_id.type == 'vas':
                vas_analytic_account = self.env['account.analytic.account'].search([('is_vas', '=', True)],limit=1)
                line.analytic_distribution = {str(vas_analytic_account.id): 100}
            if line.discount_amount:
                total = line.product_uom_qty * line.price_unit
                if total != 0:
                    line.discount = (line.discount_amount / total) * 100
            elif line.discount_amount == 0.0:
                line.discount = 0.0
