from odoo import api, fields, models, _

class MEPEquipmentSpecifications(models.Model):
    _name = "mep.equipment.specifications"
    _description = "MEP Equipment Specifications"

    crm_mep_equipment_id = fields.Many2one('crm.lead', string='CRM MEP Equipment Id')
    equipment_id = fields.Many2one('mep.equipment', string='Equipment')
    equipment_make = fields.Char(string='Make')
    equipment_qty = fields.Integer(string='Quantity', store=True)
    equipment_type = fields.Char(string='Type')
    equipment_size = fields.Integer(string='Size', store=True)



