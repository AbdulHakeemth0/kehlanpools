from odoo import api, fields, models, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError


class Lead(models.Model):
    _inherit = "crm.lead"

    pool_functionality = fields.Selection([
            ("residential", "Residential"),
            ("commercial", "Commercial"),
            ("sports", "Sports"),
            ("water", "Water Feature"),
            ("community", "Community"),
            ("government", "Government"),
            ("hospitality", "Hospitality"),
            ("others", "Others")
        ],store=True, tracking=True, copy=False)
    sub_pool_functionality = fields.Char(string="Specify") 

    no_of_pools = fields.Integer(string='No. Of Pools', tracking=True,store=True)
    pool_type = fields.Selection([
            ("swimming_pool", "Swimming Pool"),
            ("water_feature", "Water Feature"),
            ("other", "Other")],string='Pool Type', store=True)
    no_of_line_manpower = fields.Integer(string='No. of lines Manpower',store=True)
    no_of_line_consumables = fields.Integer(string='No. of lines Consumables',store=True)
    no_of_line_toolsandequipments = fields.Integer(string='No. of lines Tools and Equipments',store=True)
    no_of_line_otheritems = fields.Integer(string='No. of lines Other Items',store=True)
    profit_margin_percentage = fields.Float(string='Profit Margin %',store=True)

    total_cost = fields.Float(compute="_compute_total_cost",store=True)
    company_over_head = fields.Float(string='Company Over Head %',store=True)
    over_head = fields.Float(string='Company Over Head',store=True,compute="_compute_company_overhead")
    profit_margin = fields.Float(compute="_compute_profit_margin",store=True) 
    total_quote_amount = fields.Float(compute="_compute_total_quote_amount",store=True)


    pool_specification_ids = fields.One2many(
        string='pool specification',
        comodel_name='pool.specification.line',
        inverse_name='crm_pool_specification_id',
    )
    pool_dimension_ids = fields.One2many(
        string='pool dimension',
        comodel_name='pool.dimension',
        inverse_name='crm_pool_dimension_id',
    )
    pricing_structure_ids = fields.One2many(
        string='pricing structure',
        comodel_name='pricing.structure',
        inverse_name='crm_pricing_structure_id',
    )
    mep_equipment_ids = fields.One2many(
        string='mep equipment specifications',
        comodel_name='mep.equipment.specifications',
        inverse_name='crm_mep_equipment_id',
    )

    @api.onchange('no_of_pools')
    def _onchange_pool_dimension(self):
        if self.no_of_pools and self.no_of_pools > 0:
            self.pool_dimension_ids = [(5, 0, 0)]
            dimension_lines = []
            for pool in range(self.no_of_pools):

                dimension_lines.append((0, 0, {
                    'pool_dimension_sl_no': pool + 1,
                }))

            self.pool_dimension_ids = dimension_lines

    # @api.onchange('no_of_pools','no_of_line_manpower','no_of_line_consumables','no_of_line_toolsandequipments','no_of_line_otheritems')
    # def _onchange_no_of_pools(self):
    #     if self.no_of_pools and self.no_of_pools > 0:
            # self.pool_dimension_ids = [(5, 0, 0)]
            # self.pool_specification_ids = [(5, 0, 0)]
            # self.pricing_structure_ids = [(5, 0, 0)]
            
            # dimension_lines = []
            # specification_lines = []
            # pricing_structure_lines = []

            # for pool in range(self.no_of_pools):

                # dimension_lines.append((0, 0, {
                #     'pool_dimension_sl_no': pool + 1,
                # }))
                # specification_lines.append((0, 0, {
                #     'pool_specification_sl_no': pool + 1,
                # }))

                # pricing_structure_lines.append((0, 0, {
                #     'display_type': 'line_section',
                #     'name': f'POOL {pool + 1}',
                # }))

                # pricing_structure_lines.append((0, 0, {
                #     'display_type': 'line_section',
                #     'name': 'Manpower',
                # }))
                # for line in range(1, self.no_of_line_manpower + 1):
                #     pricing_structure_lines.append((0, 0, {
                #         'name': f'Manpower Item {line}',
                #         'pool_structure_sl_no': pool + 1,
                #         'is_manpower':True,
                #         'description': '',
                #         'unit': False,  
                #         'boq': 0.0,
                #         'unit_rate': 0.0,
                #         'amount': 0.0,
                #         'remarks': '',
                #     }))
                # pricing_structure_lines.append((0, 0, {
                #     'name': f'Total',
                #     'pool_structure_sl_no': pool + 1,
                #     'is_manpower':True,
                #     'is_sum_line':True,
                #     'boq': 0.0,
                #     'amount': 0.0,
                # }))

                # pricing_structure_lines.append((0, 0, {
                #     'display_type': 'line_section',
                #     'name': 'Consumables',  
                # }))
                # for line in range(1, self.no_of_line_consumables + 1):
                #     pricing_structure_lines.append((0, 0, {
                #         'name': f'Consumable Item {line}',
                #         'pool_structure_sl_no': pool + 1,
                #         'is_consumables':True,
                #         'description': '',
                #         'unit': False,
                #         'boq': 0.0,
                #         'unit_rate': 0.0,
                #         'amount': 0.0,
                #         'remarks': '',
                #     }))
                # pricing_structure_lines.append((0, 0, {
                #     'name': f'Total',
                #     'pool_structure_sl_no': pool + 1,
                #     'is_consumables':True,
                #     'is_sum_line':True,
                #     'boq': 0.0,
                #     'amount': 0.0,
                # }))

                # pricing_structure_lines.append((0, 0, {
                #     'display_type': 'line_section',
                #     'name': 'Tools & Equipment',
                # }))
                # for line in range(1, self.no_of_line_toolsandequipments + 1):
                #     pricing_structure_lines.append((0, 0, {
                #         'name': f'Tools & Equipment Item {line}',
                #         'pool_structure_sl_no': pool + 1,
                #         'is_toolsequipment':True,
                #         'description': '',
                #         'unit': False,
                #         'boq': 0.0,
                #         'unit_rate': 0.0,
                #         'amount': 0.0,
                #         'remarks': '',
                #     }))
                # pricing_structure_lines.append((0, 0, {
                #     'name': f'Total',
                #     'pool_structure_sl_no': pool + 1,
                #     'is_toolsequipment':True,
                #     'is_sum_line':True,
                #     'boq': 0.0,
                #     'amount': 0.0,
                # }))

                # pricing_structure_lines.append((0, 0, {
                #     'display_type': 'line_section',
                #     'name': 'Other Items',
                # }))
                # for line in range(1, self.no_of_line_otheritems + 1): 
                #     pricing_structure_lines.append((0, 0, {
                #         'name': f'Other Items Item {line}',
                #         'pool_structure_sl_no': pool + 1,
                #         'is_otheritems':True,
                #         'description': '',
                #         'unit': False, 
                #         'boq': 0.0,
                #         'unit_rate': 0.0,
                #         'amount': 0.0,
                #         'remarks': '',
                #     }))
                # pricing_structure_lines.append((0, 0, {
                #     'name': f'Total',
                #     'pool_structure_sl_no': pool + 1,
                #     'is_otheritems':True,
                #     'is_sum_line':True,
                #     'boq': 0.0,
                #     'amount': 0.0,
                # }))

            # self.pool_dimension_ids = dimension_lines
            # self.pool_specification_ids = specification_lines
            # self.pricing_structure_ids = pricing_structure_lines


    @api.onchange('no_of_pools')
    def _onchange_no_of_pools(self):
        if self.no_of_pools and self.no_of_pools > 0:
            self.pool_specification_ids = [(5, 0, 0)]

            self.pricing_structure_ids = [(5, 0, 0)]

            pricing_structure_lines = []
            specification_lines = []

            manpower_list = ['1.1 Technician','1.2 PPM Team Share','1.3 Supervisory Share','1.4 Mechanical Engineer Share','1.5 Specialist Share']
            cons_list = ['2.1 Calcium hypochlorite','2.2 Sodium bisulfate','2.3 Sodium bimetasulfate','2.4 Cyranuric acid','2.5 Chlorine tablet','2.6 Algacid','2.7 Puresan','2.8 Sodium bicarbonate']
            tool_list = ['3.1 Cleaning kit','3.2 Tool box','3.3 Miscl']
            others_list = ['4.1 Transportation','4.2 Food']

            for pool in range(self.no_of_pools):

                specification_lines.append((0, 0, {
                    'pool_specification_sl_no': pool + 1,
                }))

                pricing_structure_lines.append((0, 0, {
                    'display_type': 'line_section',
                    'name': f'POOL {pool + 1}',
                }))

                pricing_structure_lines.append((0, 0, {
                    'display_type': 'line_section',
                    'name': '1.Manpower',
                }))

                for line in range(0, len(manpower_list)):
                    pricing_structure_lines.append((0, 0, {
                        'name': manpower_list[line],
                        'pool_structure_sl_no': pool + 1,
                        'is_manpower':True,
                        'description': '',
                        'unit': False,  
                        'boq': 0.0,
                        'unit_rate': 0.0,
                        'amount': 0.0,
                        'remarks': '',
                    }))
                pricing_structure_lines.append((0, 0, {
                    'name': f'Total',
                    'pool_structure_sl_no': pool + 1,
                    'is_manpower':True,
                    'is_sum_line':True,
                    'boq': 0.0,
                    'amount': 0.0,
                }))

                pricing_structure_lines.append((0, 0, {
                    'display_type': 'line_section',
                    'name': '2.Consumables',  
                }))
                for line in range(0, len(cons_list)):
                    pricing_structure_lines.append((0, 0, {
                        'name': cons_list[line],
                        'pool_structure_sl_no': pool + 1,
                        'is_consumables':True,
                        'description': '',
                        'unit': False,
                        'boq': 0.0,
                        'unit_rate': 0.0,
                        'amount': 0.0,
                        'remarks': '',
                    }))
                pricing_structure_lines.append((0, 0, {
                    'name': f'Total',
                    'pool_structure_sl_no': pool + 1,
                    'is_consumables':True,
                    'is_sum_line':True,
                    'boq': 0.0,
                    'amount': 0.0,
                }))

                pricing_structure_lines.append((0, 0, {
                    'display_type': 'line_section',
                    'name': '3.Tools & Equipment',
                }))
                for line in range(0, len(tool_list)):
                    pricing_structure_lines.append((0, 0, {
                        'name': tool_list[line],
                        'pool_structure_sl_no': pool + 1,
                        'is_toolsequipment':True,
                        'description': '',
                        'unit': False,
                        'boq': 0.0,
                        'unit_rate': 0.0,
                        'amount': 0.0,
                        'remarks': '',
                    }))
                pricing_structure_lines.append((0, 0, {
                    'name': f'Total',
                    'pool_structure_sl_no': pool + 1,
                    'is_toolsequipment':True,
                    'is_sum_line':True,
                    'boq': 0.0,
                    'amount': 0.0,
                }))

                pricing_structure_lines.append((0, 0, {
                    'display_type': 'line_section',
                    'name': '4.Other Items',
                }))
                for line in range(0, len(others_list)): 
                    pricing_structure_lines.append((0, 0, {
                        'name': others_list[line],
                        'pool_structure_sl_no': pool + 1,
                        'is_otheritems':True,
                        'description': '',
                        'unit': False, 
                        'boq': 0.0,
                        'unit_rate': 0.0,
                        'amount': 0.0,
                        'remarks': '',
                    }))
                pricing_structure_lines.append((0, 0, {
                    'name': f'Total',
                    'pool_structure_sl_no': pool + 1,
                    'is_otheritems':True,
                    'is_sum_line':True,
                    'boq': 0.0,
                    'amount': 0.0,
                }))
            self.pricing_structure_ids = pricing_structure_lines
            self.pool_specification_ids = specification_lines

    @api.onchange('pricing_structure_ids')
    def _onchange_total(self):
        total_amount = 0
        total_boq = 0  
        
        for record in self.pricing_structure_ids:
            if record.display_type == 'line_section':
                pass

            elif not record.display_type == 'line_section' and not record.is_sum_line:
                total_amount += record.amount
                total_boq += record.boq

            elif record.is_sum_line:  
                record.boq = total_boq

                t_amount = total_amount * self.profit_margin_percentage
                p_amount = t_amount / 100
                record.amount = total_amount + p_amount  
                
                total_amount = 0
                total_boq = 0

 
    @api.depends('pricing_structure_ids') 
    def _compute_total_cost(self):
        for lead in self:
            total = 0
            for pricing in lead.pricing_structure_ids:
                if pricing.display_name == 'Total':
                    total += pricing.amount
            lead.total_cost = total

    @api.depends('company_over_head','total_cost')
    def _compute_company_overhead(self):
        for lead in self:
            if lead.total_cost:
                over_head = (lead.total_cost) * (lead.company_over_head)
                lead.over_head = over_head/100
            else:
                lead.over_head = 0


    @api.depends('total_cost')
    def _compute_profit_margin(self):
        for lead in self:
            if lead.total_cost:
                t_amount = (lead.total_cost) * (self.profit_margin_percentage)
                lead.profit_margin = t_amount/100
            else:
                lead.profit_margin = 0

    @api.depends('total_cost', 'company_over_head', 'profit_margin')
    def _compute_total_quote_amount(self):
        for lead in self:
            company_overhead = (lead.total_cost * lead.company_over_head / 100) if lead.total_cost else 0
            lead.total_quote_amount = lead.total_cost + company_overhead + lead.profit_margin



    def action_new_quotation(self):
        action = super(Lead, self).action_new_quotation()
        
        sale_pool_specification_line = []
        for line in self.pool_specification_ids:
            if line.pool_specification_sl_no:
                sale_pool_specification_line.append((0, 0, {
                    'pool_specification_sl_no' : line.pool_specification_sl_no,
                    'area_of_pool' : line.area_of_pool,
                    'volume_of_water' : line.volume_of_water,
                    'filteration_system' : line.filteration_system,
                    'asset_location':line.asset_location,
                    'auto_dozing_system' : line.auto_dozing_system, 
                    'disinfection_system' : line.disinfection_system, 
                    'pool_loc':line.pool_loc,
                    'pool_finishing_type' : line.pool_finishing_type, 
                    'age_of_pool' : line.age_of_pool, 
                    'distance_from_camp' : line.distance_from_camp, 
                    'distance_from_other_pools' : line.distance_from_other_pools, 
                    'pools_in_circuit' : line.pools_in_circuit, 
                    'visit_frequency' : line.visit_frequency, 
                    'visit_type' : line.visit_type,
                    'accomodation' : line.accomodation, 
                }))

        action['context']['default_pool_functionality'] = self.pool_functionality
        if self.sub_pool_functionality:
            action['context']['default_sub_pool_functionality'] = self.sub_pool_functionality
        action['context']['default_no_of_pools'] = self.no_of_pools
        if self.pool_type:
            action['context']['default_pool_type'] = self.pool_type

        if sale_pool_specification_line:
            action['context']['default_pool_specification_ids'] = sale_pool_specification_line

        sale_pool_dimension_line = []
        for line in self.pool_dimension_ids:
            if line.pool_dimension_sl_no:
                sale_pool_dimension_line.append((0, 0, {
                    'pool_dimension_sl_no' : line.pool_dimension_sl_no,
                    'length' : line.length,
                    'breadth' : line.breadth,
                    'pool_depth' : line.pool_depth,
                    'water_depth' : line.water_depth,
                    'water_volume' : line.water_volume,
                    'pool_surface_area' : line.pool_surface_area,
                    'coping_width' : line.coping_width,
                    'coping_surface_area' : line.coping_surface_area,
                    'total_surface_area' : line.total_surface_area,
                }))
        if sale_pool_dimension_line:
            action['context']['default_pool_dimension_ids'] = sale_pool_dimension_line


        sale_pool_structure_line = []
        for line in self.pricing_structure_ids:
            if line.display_name and line.display_type == 'line_section':
                sale_pool_structure_line.append((0, 0, {
                    'display_type': 'line_section',
                    'name': line.display_name,
                }))
            if line.display_name == 'Total':
                sale_pool_structure_line.append((0, 0, {
                    'item_master_id' : line.item_master_id.id,
                    'pool_structure_sl_no' : line.pool_structure_sl_no,
                    'name' : line.name,
                    'description' : line.description,
                    'unit' : line.unit.id,
                    'boq' : line.boq,
                    'unit_rate' : line.unit_rate,
                    'amount' : line.amount,
                    'is_sum_line':True,
                    'total_amount' : line.total_amount,
                    'remarks' : line.remarks,
                    'out_of' : line.out_of,
                }))
            elif line.pool_structure_sl_no:
                sale_pool_structure_line.append((0, 0, {
                    'item_master_id' : line.item_master_id.id,
                    'pool_structure_sl_no' : line.pool_structure_sl_no,
                    'name' : line.name,
                    'description' : line.description,
                    'unit' : line.unit.id,
                    'boq' : line.boq,
                    'unit_rate' : line.unit_rate,
                    'amount' : line.amount,
                    'total_amount' : line.total_amount,
                    'remarks' : line.remarks,
                    'out_of' : line.out_of,
                }))

                # pricing_structure_sale_order_line = []
                # pricing_structure_sale_order_line.append((0, 0, {
                #     'product_template_id' : line.name,
                #     'product_uom' : line.unit,
                #     'price_subtotal' : line.amount,
                #     'unit_rate' : line.unit_rate,
                #     'amount' : line.amount,
                # }))

        action['context']['default_profit_margin_percentage'] = self.profit_margin_percentage
        action['context']['default_company_over_head'] = self.company_over_head
        action['context']['default_no_of_line_manpower'] = self.no_of_line_manpower
        action['context']['default_no_of_line_consumables'] = self.no_of_line_consumables
        action['context']['default_no_of_line_toolsandequipments'] = self.no_of_line_toolsandequipments
        action['context']['default_no_of_line_otheritems'] = self.no_of_line_otheritems

        if sale_pool_structure_line:
            action['context']['default_pricing_structure_ids'] = sale_pool_structure_line
        # action['context']['default_sale_order_line'] = pricing_structure_sale_order_line


        sale_mep_equipment_line = []
        for line in self.mep_equipment_ids:
            if line.equipment_id:
                sale_mep_equipment_line.append((0, 0, {
                    'equipment_id' : line.equipment_id.id,
                    'equipment_make' : line.equipment_make, 
                    'equipment_type' : line.equipment_type,
                    'equipment_size' : line.equipment_size,
                }))

        if sale_mep_equipment_line:
            action['context']['default_mep_equipment_ids'] = sale_mep_equipment_line

        return action

    def action_sale_quotations_new(self):
        res = super(Lead, self).action_sale_quotations_new()
        for rec in self:
            users = self.env['hr.employee'].sudo().search([]).filtered(lambda l:l.job_id.is_sales_executive or l.job_id.is_sales_engineer).user_id
            model = self.env["ir.model"].sudo().search([("model", "=", "crm.lead")],limit=1)     
            for each_user in users:
                data = {
                    "res_id": rec.id,
                    "res_model_id": model.id,
                    "user_id": each_user.id,
                    "summary": _(('New Quotation has been created-%s') % (
                                    str( self.env.user.name))),
                    "activity_type_id": self.env.ref("bi_crm.quotation_notify_activity_id").id
                }
                self.env["mail.activity"].sudo().create(data)
        return res