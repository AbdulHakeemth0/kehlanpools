from odoo import api, fields, models, _


class PoolDimension(models.Model):
    _name = "pool.dimension"
    _description = "pool dimension"

    crm_pool_dimension_id = fields.Many2one(string='crm pool dimension id',comodel_name='crm.lead')

    pool_dimension_sl_no = fields.Integer(string='Pool No',store=True)
    length = fields.Float(string='Length',store=True)
    breadth = fields.Float(string='Breadth',store=True)
    pool_depth = fields.Float(string='Pool Depth',store=True)
    water_depth = fields.Float(string='Water Depth',store=True)
    water_volume = fields.Float(string='Water Volume', compute='_compute_pool_dimension', store=True)
    pool_surface_area = fields.Float(string='Pool Surface Area', compute='_compute_pool_dimension', store=True)
    coping_width = fields.Float(string='Coping Width')
    coping_surface_area = fields.Float(string='Coping Surface Area', compute='_compute_pool_dimension', store=True)
    total_surface_area = fields.Float(string='Total Surface Area', compute='_compute_pool_dimension', store=True)


    @api.depends('length', 'breadth', 'water_depth', 'pool_depth', 'coping_width')
    def _compute_pool_dimension(self):
        for record in self:
            record.water_volume = 0.0
            record.pool_surface_area = 0.0
            record.coping_surface_area = 0.0
            record.total_surface_area = 0.0
            
            if record.length and record.breadth and record.water_depth:
                record.water_volume = record.length * record.breadth * record.water_depth

            if record.length and record.breadth and record.pool_depth:
                record.pool_surface_area = (
                    record.length * record.breadth
                    + 2 * (record.length * record.pool_depth + record.breadth * record.pool_depth)
                )

            if record.length and record.breadth and record.coping_width:
                record.coping_surface_area = record.coping_width * 2 * (record.length + record.breadth)

            if record.pool_surface_area and record.coping_surface_area:
                record.total_surface_area = record.pool_surface_area + record.coping_surface_area


