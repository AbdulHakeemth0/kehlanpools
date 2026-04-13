from odoo import api, fields, models, _


class SaleChemicalUseLine(models.Model):
    _name = "sale.chemical.use.line"
    _description = "Sale Chemical Use Line"

    sale_order_id = fields.Many2one(string='sale chemical use line',comodel_name='sale.order')
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
    