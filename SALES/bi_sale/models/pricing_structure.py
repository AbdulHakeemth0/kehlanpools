from odoo import api, fields, models, _


class PricingStructureSale(models.Model):
    _name = "pricing.structure.sale"
    _description = "pricing structure sale"

    sale_pricing_structure_id = fields.Many2one(string='sale pricing structure id',comodel_name='sale.order')
    item_master_id = fields.Many2one(string='Items',comodel_name='item.master',store=True)

    pool_structure_sl_no = fields.Integer(string='Pool No', store=True)
    name = fields.Char(string='Name',store=True)
    description = fields.Char(string='Description',store=True)
    unit = fields.Many2one(string='Unit',comodel_name='uom.uom',store=True)
    boq = fields.Float(string='BOQ',store=True,default=1.0,digits=(16, 3))
    unit_rate = fields.Float(string='Unit Rate/Month',store=True,digits=(16, 3))
    amount = fields.Float(string='Amount/Month', compute='_compute_amount',store=True,digits=(16, 3))
    total_amount = fields.Float(string='Total Amount/Month', store=True)
    remarks = fields.Text(string='Remarks',store=True)
    out_of = fields.Integer(string='Out Of',default=lambda self: 1,store=True)
    display_type = fields.Selection(
    selection=[
        ('line_section', "Section"),
    ],
    default=False,store=True)
    is_manpower = fields.Boolean(string='Is Manpower', default=False)
    is_consumables = fields.Boolean(string='Is Consumables', default=False)
    is_toolsequipment = fields.Boolean(string='Is Tools and Equipment', default=False)
    is_otheritems = fields.Boolean(string='Is Other Items', default=False)
    is_sum_line = fields.Boolean(string='Is Sum Line', default=False)

    @api.depends('boq','unit_rate','sale_pricing_structure_id')
    def _compute_amount(self):
        # if self.sale_pricing_structure_id.profit_margin_percentage > 0:
        #     for record in self:
        #         t_amount = (record.boq) * (record.unit_rate)
        #         p_amount = (t_amount) * (self.sale_pricing_structure_id.profit_margin_percentage)
        #         r_amount = p_amount/100
        #         record.amount = (t_amount) + (r_amount)
        # else:
        for record in self:
            if not record.display_name == "Total":
                record.amount = (record.boq) * (record.unit_rate)  

    @api.onchange('item_master_id')
    def _onchange_boq(self):
        for record in self:
            if record.item_master_id.is_technician:
                total_boq = 0.0
                for line in record.sale_pricing_structure_id.pool_specification_ids:
                    if line.pool_specification_sl_no == record.pool_structure_sl_no:
                        total_boq += (line.area_of_pool * line.visit_frequency) / 80
                record.boq = total_boq

            if record.item_master_id.is_supervisory_share:
                total_boq = 0.0
                for line in record.sale_pricing_structure_id.pool_specification_ids:
                    if line.pool_specification_sl_no == record.pool_structure_sl_no:
                        total_boq += (line.visit_frequency /8)
                record.boq = total_boq


    @api.onchange('out_of')
    def _onchange_out_of(self):
        for record in self:
            for line in record.sale_pricing_structure_id.pool_specification_ids:
                if line.pool_specification_sl_no == record.pool_structure_sl_no:
                    record.boq = line.volume_of_water / record.out_of

