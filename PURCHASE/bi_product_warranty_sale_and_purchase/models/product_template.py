from odoo import models, fields, _ ,api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    warranty_type = fields.Selection(
        [('civil', 'Civil'), ('mep', 'MEP')],
        string="Warranty Type", store=True
    )
    is_civil_warranty_type = fields.Boolean(string="Is Civil Warranty Type", compute="_compute_warranty_visibility",
                                            store=True)
    is_mep_warranty_type = fields.Boolean(string="Is MEP Warranty Type", compute="_compute_warranty_visibility",
                                          store=True)

    purchase_warranty = fields.Float(string = "Purchase warranty", tracking=True)
    purchase_warranty_period = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Purchase Warranty Period", copy=False, tracking=True)
    sale_warranty = fields.Float(string ="MEP warranty", tracking=True)
    sale_warranty_period = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="MEP Warranty Period", tracking=True, copy=False)

    # Civil warranty fields
    civil_warranty = fields.Float(string="Civil Warranty", tracking=True)
    civil_warranty_period = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Civil Warranty Period", tracking=True, copy=False)

    pw_count = fields.Integer(compute="_compute_pw_count", string='')
    sw_count = fields.Integer(compute = "_compute_sw_count",string = 'MEP Warranty Count')
    cw_count = fields.Integer(compute="_compute_cw_count", string="Civil Warranty Count")

    @api.depends('warranty_type')
    def _compute_warranty_visibility(self):
        for record in self:
            if record.warranty_type == 'civil':
                record.is_civil_warranty_type = True
                record.is_mep_warranty_type = False
            elif record.warranty_type == 'mep':
                record.is_civil_warranty_type = False
                record.is_mep_warranty_type = True

    def view_purchase_warranty(self):
        self.ensure_one()
        for rec in self:
            action = {
                    'type': 'ir.actions.act_window',
                    'name': _('Purchase warranty'),
                    'domain': [('product_id', '=', rec.id),('picking_type','=','incoming')],
                    'res_model': 'product.warranty',
                    'views': [(False, 'list'),(False, 'form'),(False, 'kanban')],
                    'view_mode': 'list,form,kanban',
                    'target':"current"
                    }
        return action
    
    def view_sale_warranty(self):
        self.ensure_one()
        for rec in self:
            action = {
                    'type': 'ir.actions.act_window',
                    'name': _('Sale warranty'),
                    'domain': [('product_id', '=', rec.id),('picking_type','=','outgoing')],
                    'res_model': 'product.warranty',
                    'views': [(False, 'list'),(False, 'form'),(False, 'kanban')],
                    'view_mode': 'list,form,kanban',
                    'target':"current"
                    }
        return action

    
    def _compute_pw_count(self):
        for rec in self:
            res = self.env['product.warranty'].search_count([('product_id', '=', rec.id),('picking_type','=','incoming')])
            rec.pw_count = res or 0  
            
    def _compute_sw_count(self):
        for rec in self:
            res = self.env['product.warranty'].search_count([('product_id', '=', rec.id),('picking_type','=','outgoing')])
            rec.sw_count = res or 0

    # Compute method for civil warranty count
    def _compute_cw_count(self):
        for rec in self:
            res = self.env['product.warranty'].search_count([('product_id', '=', rec.id)])
            rec.cw_count = res or 0