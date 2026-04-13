from odoo import api, fields, models, _


class ItemMaster(models.Model):
    _name = 'item.master'
    _description = 'item master'
    _rec_name = 'item'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    item = fields.Char(string='Item')
    
    is_technician = fields.Boolean(string='is technician', tracking=True,store=True)
    is_supervisory_share = fields.Boolean(string='is supervisory share', tracking=True,store=True)
    