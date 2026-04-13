# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil import relativedelta

from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError

class MEPEquipment(models.Model):
    _name = 'mep.equipment'
    _description = 'MEP Equipment'

    name = fields.Char(string="Equipment Name", required=True)