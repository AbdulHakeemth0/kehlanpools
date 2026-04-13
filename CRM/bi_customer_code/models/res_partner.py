from odoo import models, fields,api,_
from odoo.exceptions import UserError, ValidationError



class ResPartner(models.Model):
    _inherit = "res.partner"
    _rec_names_search = ['complete_name', 'email', 'ref', 'vat', 'company_registry','code']

    code = fields.Char(string="M-Number",tracking=True)
    customer_profile = fields.Selection([
                            ('vip', 'VIP'),
                            ('general', 'General'),
                        ], string="Profile")
    customer_type = fields.Selection([
                            ('individual', 'Individual'),
                            ('community', 'Community'),
                            ('hospitality', 'Hospitality'),
                            ('commercial', 'Commercial'),
                            ('govt', 'Govt'),
                        ], string="Customer Type")
    
    @api.constrains('code')
    def _check_code_exist(self):
        for record in self:
            if record.code:
                rec = self.env['res.partner'].search([('code', '=', record.code)])
                if len(rec)>1:
                    raise UserError(_('This M-Number is already assigned to another customer'))

    # @api.model_create_multi
    # def create(self, vals_list):
    #     res = super().create(vals_list)
    #     if res.customer_rank:
    #         res.code = self.env['ir.sequence'].next_by_code('customer.code') or _('New')
    #     return res