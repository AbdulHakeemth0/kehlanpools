# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class CreateRFQ(models.TransientModel):
    _name = 'create.rfq'
    _description = 'Create RFQ'

    vendor_ids = fields.Many2one('res.partner', string='Vendors')
    purchase_requisition_id = fields.Many2one('bi.purchase.order', string='Purchase Requisition')
