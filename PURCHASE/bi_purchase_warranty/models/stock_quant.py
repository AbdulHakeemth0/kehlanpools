from odoo import models, fields, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    number_of_warranty = fields.Float(string="Warranty")
    warranty_type = fields.Selection([
        ('days', 'Days'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Warranty Period")

    @api.model_create_multi
    def create(self, vals_list):
        """
        function used to when tracking is 'None' added warranty on product,
        when tracking is serial or lot added warranty on stock (stock.quant)
        Args:
            vals_list:
        Returns:
        """
        res = super(StockQuant, self).create(vals_list)
        ctx = self._context
        if 'button_validate_picking_ids' in ctx:
            picking = ctx['button_validate_picking_ids'][0]
            picking_id = self.env['stock.picking'].browse(picking)
            purchase_id = picking_id.purchase_id
            if picking_id:
                lines = picking_id.move_ids.filtered(lambda x: x.warranty > 0)
                if lines:
                    for rec in res:
                        line_warranty = lines.filtered(lambda x: x.product_id == rec.product_id)
                        if line_warranty:
                            if rec.product_id.tracking == 'none' and purchase_id:
                                existing_warranty = rec.product_id.template_warranty_ids.filtered(
                                    lambda x: x.partner_id == purchase_id.partner_id)
                                if existing_warranty:
                                    existing_warranty.update({
                                        'number_of_warranty': line_warranty.warranty,
                                        'warranty_type': line_warranty.warranty_type
                                    })
                                else:
                                    rec.product_id.template_warranty_ids = [(0, 0, {
                                        'number_of_warranty': line_warranty.warranty,
                                        'warranty_type': line_warranty.warranty_type,
                                        'partner_id': purchase_id.partner_id.id
                                    })]
                            else:
                                rec.number_of_warranty = line_warranty.warranty
                                rec.warranty_type = line_warranty.warranty_type
        return res

    def write(self, vals):
        """
        function used to when tracking is 'None' added warranty on product,
        when tracking is serial or lot added warranty on stock (stock.quant)
        Args:
            vals:
        Returns:
        """
        res = super(StockQuant, self).write(vals)
        ctx = self._context
        if 'button_validate_picking_ids' in ctx:
            picking = ctx['button_validate_picking_ids'][0]
            picking_id = self.env['stock.picking'].browse(picking)
            purchase_id = picking_id.purchase_id
            if picking_id:
                lines = picking_id.move_ids.filtered(lambda x: x.warranty > 0)
                if lines:
                    for rec in self:
                        line_warranty = lines.filtered(lambda x: x.product_id == rec.product_id)
                        if line_warranty and purchase_id:
                            if rec.product_id.tracking == 'none':
                                    existing_warranty = rec.product_id.template_warranty_ids.filtered(
                                        lambda x: x.partner_id == purchase_id.partner_id)
                                    if existing_warranty:
                                        existing_warranty.update({
                                            'number_of_warranty': line_warranty.warranty,
                                            'warranty_type': line_warranty.warranty_type
                                        })
                                    else:
                                        rec.product_id.template_warranty_ids = [(0, 0, {
                                            'number_of_warranty': line_warranty.warranty,
                                            'warranty_type': line_warranty.warranty_type,
                                            'partner_id': purchase_id.partner_id.id
                                        })]
                            else:
                                existing_warranty = rec.product_id.template_warranty_ids.filtered(
                                    lambda x: x.partner_id == purchase_id.partner_id)
                                if existing_warranty:
                                    existing_warranty.update({
                                        'number_of_warranty': line_warranty.warranty,
                                        'warranty_type': line_warranty.warranty_type
                                    })
                                else:
                                    rec.product_id.template_warranty_ids = [(0, 0, {
                                        'number_of_warranty': line_warranty.warranty,
                                        'warranty_type': line_warranty.warranty_type,
                                        'partner_id': purchase_id.partner_id.id
                                    })]    
        return res                                                                                                                    
