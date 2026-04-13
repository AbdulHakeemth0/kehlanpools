from odoo import fields, models
from odoo.tools import SQL


class DiscountSaleReport(models.Model):
    """This class inherits 'sale.report' and adds field discount"""
    _inherit = 'sale.report'

    # discount = fields.Float('Discount', readonly=True,
    #                         help="Specify the discount amount.")
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account")
    

    def _select_additional_fields(self):
        res = super()._select_additional_fields()

        res['analytic_account_id'] = "s.analytic_account_id"

        return res
    
    def _group_by_sale(self):
        """
        This method adds custom fields (including distribution_analytic_account_ids) 
        to the GROUP BY clause of the report.
        """
        res = super()._group_by_sale()

        res += """, s.analytic_account_id"""

        return res
    
    # def _select(self) -> SQL:
    #     """It extends the behavior of a method in the class by adding a
    #         new column, discount, to the SQL query. This new column represents
    #         the total discount for sales transactions, calculated based on
    #         various factors and values related to the sale. """
    #     return SQL(
    #         "%s, sum(l.product_uom_qty / u.factor * u2.factor * cr.rate * l.price_unit * l.discount / 100.0) as discount",
    #         super()._select())
