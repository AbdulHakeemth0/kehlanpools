from odoo import api, fields, models, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class DamageImage(models.Model):
    _name = 'damage.image'
    _description = 'Damage Image Master'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    image_save_1 = fields.Image(
    string='Front view', tracking=True,
    )
    image_save_2 = fields.Image(
    string='Right Side view', tracking=True,
    )
    image_save_3 = fields.Image(
    string='Left Side view', tracking=True,
    )
    image_save_4 = fields.Image(
    string='Rear view', tracking=True,
    )
