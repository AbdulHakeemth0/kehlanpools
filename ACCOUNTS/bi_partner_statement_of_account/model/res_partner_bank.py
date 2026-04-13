# -*- coding: utf-8 -*-

import logging

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    _rec_name = 'iban_number'

    iban_number = fields.Char(string='IBAN Number')
    swift_code = fields.Char(string='Swift Code')