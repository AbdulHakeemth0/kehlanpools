from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_amc_report(self):
       return self.env.ref('bi_swimming_pool_report.action_swimming_pool_report').report_action(self)