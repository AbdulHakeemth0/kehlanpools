# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil import relativedelta

from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError


class HelpDeskStage(models.Model):
    _inherit = 'helpdesk.stage'


    is_assign = fields.Boolean(string="Is Assign")
    is_hold = fields.Boolean(string="Is Hold")
    is_solved = fields.Boolean(string="Is Solved")
    is_cancel = fields.Boolean(string="Is Cancel")



    