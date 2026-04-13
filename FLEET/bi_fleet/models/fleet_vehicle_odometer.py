from odoo import api, fields, models, _
from lxml import etree

class FleetVehicleOdometer(models.Model):
    _inherit = 'fleet.vehicle.odometer'

    starting_odometer_value = fields.Float(string='Starting Km', aggregator="max")
    ending_odometer_value = fields.Float(string='Ending Km', aggregator="max")

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options)
        views_type = ['form', 'kanban', 'list']
        for type in views_type:
            arch = res['views'].get(type, {}).get('arch')
            if arch:
                if self.env.user.has_groups('bi_fleet.odometer_access_group'):
                    tree = etree.fromstring(arch)
                    for node in tree.xpath('//'+type):
                        node.set('create', 'true')
                        node.set('edit', 'true')
                    arch = etree.tostring(tree, encoding='unicode')
                else:
                    tree = etree.fromstring(arch)
                    for node in tree.xpath('//'+type):
                        node.set('create', 'false')
                        node.set('edit', 'false')
                    arch = etree.tostring(tree, encoding='unicode')
                res['views'][type]['arch'] = arch
        return res
    
    @api.onchange('starting_odometer_value', 'ending_odometer_value')
    def _onchange_odometer_value(self):
        self.ensure_one()
        if self.starting_odometer_value or self.ending_odometer_value:
            self.value = self.ending_odometer_value - self.starting_odometer_value

