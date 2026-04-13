from odoo import api, fields, models, _


class PoolSpecificationLine(models.Model):
    _name = "pool.specification.line"
    _description = "pool specification line"

    crm_pool_specification_id = fields.Many2one(string='pool specification id',comodel_name='crm.lead')

    pool_specification_sl_no = fields.Integer(string='Pool No', store=True)
    area_of_pool = fields.Float(string='Area of Pool',store=True, compute='_compute_pool_specification')
    location_of_pool = fields.Char(string='Location of Pool', store=True)
    pool_loc = fields.Selection([
            ("backyard", "Backyard"),
            ("front", "Front yard"),
            ("roof", "Roof top"),
            ("basement", "Basement"),
            ("other", "Other")],string='Pool Location', store=True)
    volume_of_water = fields.Float(string='Volume of water',store=True, compute='_compute_pool_specification')
    pool_filteration_system = fields.Float(string='Pool filtration System',store=True)
    filteration_system = fields.Selection([
            ("firtrinov", "Fitrinov"),
            ("skimmer", "Skimmer"),
            ("overflow", "Overflow"),
            ("infinity", "Infinity"),
            ("other", "Other"),
        ],string='Filteration System', store=True) 
    asset_location = fields.Selection([
            ("indoor", "Indoor"),
            ("outdoor", "Outdoor"),
            ("other", "Other"),
        ],string='Asset Location', store=True) 
    auto_dozing_system = fields.Selection([
            ("yes", "Yes"),
            ("na", "NA"),
        ],string='Auto Dozing System', store=True)
    disinfection_system = fields.Selection([
            ("yes", "Yes"),
            ("na", "NA"),
        ],string='Disinfection System', store=True)
    pool_finishing_type = fields.Selection([
            ("tiles", "Tiles"),
            ("grp", "GRP"),
            ("sheet", "Sheet"),
            ("other", "other"),
        ],string='Pool finishing type', store=True)    
    age_of_pool = fields.Float(string='Age of Pool',store=True)
    distance_from_camp = fields.Float(string='Distance from Camp (km)',store=True)
    distance_from_other_pools = fields.Float(string='Distance from other pools (km)',store=True)
    pools_in_circuit = fields.Char(string='No. Of pools in the circuit',store=True)
    visit_frequency = fields.Float(string='Visit Frequency ',store=True)
    visit_type = fields.Selection([
            ("weekly", "Weekly"),
            ("monthly", "Monthly"),
            ("yearly", "Yearly"),
        ],string='Visit Type', store=True)
    sub_visit_type = fields.Char(string="Specify") 

    accomodation = fields.Selection([
            ("yes", "Yes"),
            ("na", "NA")
        ],string='Accommodation provided?', store=True)
    
    @api.depends('area_of_pool', 'volume_of_water', 'crm_pool_specification_id.pool_dimension_ids')
    def _compute_pool_specification(self):
        for record in self:
            record.area_of_pool = 0.0
            record.volume_of_water = 0.0

            for line in record.crm_pool_specification_id.pool_dimension_ids:
                for each_line in record.crm_pool_specification_id.pool_specification_ids:
                    if line.pool_dimension_sl_no == each_line.pool_specification_sl_no:
                        each_line.volume_of_water = line.water_volume if line.water_volume else 0.0
                        each_line.area_of_pool = line.total_surface_area if line.total_surface_area else 0.0
                
