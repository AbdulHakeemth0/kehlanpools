from odoo import models, fields, api 

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    job_number = fields.Many2one("sale.order", string="Job number")

    @api.onchange('job_number')
    def _onchange_job_number(self):
        for order in self:
            project_id = self.env['project.project'].search([('order_id', '=', self.job_number.id)])
                
            if project_id:
                    for line in order.order_line:
                        line.analytic_distribution = {project_id.id: 100} 
            else:
               for line in order.order_line:
                        line.analytic_distribution = ''
                        
