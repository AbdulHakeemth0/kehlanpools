from odoo import api, fields, models, _
from lxml import etree

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    image_1 = fields.Image(default=lambda self: self._get_image_1_field())
    image_2 = fields.Image(default=lambda self: self._get_image_2_field())
    image_3 = fields.Image(default=lambda self: self._get_image_3_field())
    image_4 = fields.Image(default=lambda self: self._get_image_4_field())
    image_1_damage_ids = fields.One2many('fleet.vehicle.damages.description', 'image_1_vehicle_id', string='Damages Description')
    image_2_damage_ids = fields.One2many('fleet.vehicle.damages.description', 'image_2_vehicle_id', string='Damages Description ')
    image_3_damage_ids = fields.One2many('fleet.vehicle.damages.description', 'image_3_vehicle_id', string='Damages Description  ')
    image_4_damage_ids = fields.One2many('fleet.vehicle.damages.description', 'image_4_vehicle_id', string='Damages Description   ')
    documents_count = fields.Integer(compute='_compute_documents_count', string='Documents  ')
    starting_odometer = fields.Float(compute='_get_starting_odometer', string='Starting Odometer')

    # default=lambda self: self._get_image_field()
    @api.model
    def _get_image_1_field(self):
        related_record = self.env['damage.image'].search([('image_save_1', '!=', False)], limit=1)
        if related_record:
            return related_record.image_save_1
        return False

    @api.model
    def _get_image_2_field(self):
        related_record = self.env['damage.image'].search([('image_save_2', '!=', False)], limit=1)
        if related_record:
            return related_record.image_save_2
        return False
        
    @api.model
    def _get_image_3_field(self):
        related_record = self.env['damage.image'].search([('image_save_3', '!=', False)], limit=1)
        if related_record:
            return related_record.image_save_3
        return False

    @api.model
    def _get_image_4_field(self):
        related_record = self.env['damage.image'].search([('image_save_4', '!=', False)], limit=1)
        if related_record:
            return related_record.image_save_4
        return False

    @api.model
    def get_views(self, views, options=None):
        res = super().get_views(views, options=options)
        if "form" in res["views"]:
            arch = res["views"]["form"]["arch"]
            doc = etree.fromstring(arch)
            if not self.env.user.has_groups('bi_fleet.odometer_access_group'):
                for node in doc.xpath("//div[@class='o_row o_hr_narrow_field']"):
                    for field in node.xpath(".//field[@name='odometer']"):
                        field.attrib["readonly"] = "1"
                    for field in node.xpath(".//field[@name='odometer_unit']"):
                        field.attrib["readonly"] = "1"
                arch = etree.tostring(doc, encoding="unicode")
                res["views"]["form"]["arch"] = arch
        return res

    @api.model
    def _get_starting_odometer(self):
        FleetVehicalOdometercustom = self.env['fleet.vehicle.odometer'].sudo().search([])
        for record in self:
            vehicle_starting_odometer = FleetVehicalOdometercustom.sudo().search([('vehicle_id', '=', record.id)], limit=1, order='starting_odometer_value desc')
            if vehicle_starting_odometer:
                record.starting_odometer = vehicle_starting_odometer.starting_odometer_value
            else:
                record.starting_odometer = 0

    def action_attachments(self):
        self.ensure_one()
        return {
            'name': _('Documents'),
            'domain': [('vehicle_id', '=', self.id)],
            'res_model': 'vehicle.document',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': {'default_vehicle_id': self.id}
        }
    
    def _compute_documents_count(self):
        for rec in self:
            rec.documents_count = self.env['vehicle.document'].search_count(
                [('vehicle_id', '=', rec.id)])


class FleetVehicleDamagesDescription(models.Model):
    _name = 'fleet.vehicle.damages.description'
    _description = 'Fleet Vehicle Damages Description'

    comments = fields.Text(string='Comments')
    date = fields.Date(string="Date")
    name = fields.Char(string='Name')
    image_1_vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    image_2_vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle ')
    image_3_vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle  ')
    image_4_vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle   ')
