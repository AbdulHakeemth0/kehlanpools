from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero, float_compare
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import AccessError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
        
    vas_warranty_ids = fields.One2many('warranty.vas.exclusion', 'sale_id', string="Vas Warranties")
    scope_of_work_ids = fields.One2many('scope.of.work.page', 'sale_id', string="General Scope of Work  ")

    vas_temp_amount = fields.Boolean(string="Is Amount",compute="_compute_section_and_note_sum")
    type = fields.Selection([
        ('vas', 'VAS'),
        ('amc', 'AMC'),
    ], string="Type", required=True, tracking=True)
    amc_count = fields.Integer(compute='_compute_get_amc')

    project_ids = fields.One2many(
        'project.project',
        'order_id',
        string='Projects',
        store=True,
    )
    is_not_latest_revision = fields.Boolean("Is not latest revision", default=False)

#     state = fields.Selection(
#         selection=[
#     ('draft', "Quotation"),
#     ('sent', "Quotation Sent"),
#     ('revise', "Revised"),
#     ('sale', "Sales Order"),
#     ('cancel', "Cancelled"),
# ],
#         string="Status",
#         readonly=True, copy=False, index=True,
#         tracking=3,
#         default='draft')





    
    state = fields.Selection(selection_add=[('draft','Quotation'),('submitted', 'Submitted For Approval'),('approved', 'Approved'),('sent','Quotation Sent'),('sale','Sale Order'),('revise', 'Revised')], ondelete={'revise': 'set default'})

    revision_number = fields.Integer(string="VAS Revision", default=0)
    original_sale_order_id = fields.Many2one('sale.order', string="Original Sale Order")
    is_revision = fields.Boolean(string="Is VAS Revision", default=False)
    is_amc = fields.Boolean(string="Is AMC Revision", default=False, compute = "_compute_is_amc")
    amc_start_date = fields.Date(string="AMC Start Date")
    amc_end_date = fields.Date(string="AMC End Date")
    amc_revision_number = fields.Integer(string="AMC Revision", default=0)
    visit_freq = fields.Float(string="Frequency of visit")
    
    sale_revision_ids = fields.One2many('sale.revision','sale_order_id', string = "Sale Revision")
    detailed_specification_ids = fields.One2many('detailed.specification', 'sale_id', string="Detailed Specification")
    client_exclusions_ids = fields.One2many('client.exclusion.line', 'sale_id', string="Exclusions")
    warranty_details_ids = fields.One2many('warranty.details.line', 'sale_id', string="Warranty Details")
    vas_warranty_details_ids = fields.One2many('vas.warranty.exclusion.line','sale_id', string="Vas Warranty Details" )
    payment_term_vas_ids = fields.One2many('payment.term.vas' , 'sale_id', string='Payment Terms ')
    warranty_exclusion = fields.Html(string="Warranty Exclusion")
    completion_period = fields.Text(string="Completion Period")
    contract_end_date = fields.Date(string="Contract End Date")
    contract_start_date = fields.Date(string="Contract Start Date")
    product_ids = fields.Binary(string="  ")
    is_revise =fields.Boolean("Is Revise", deafult=False) 

    @api.depends('vas_temp_amount')
    def _compute_section_and_note_sum(self):
        """
        Compute section and note sums for the last line of a section or note.
        """
        value1 = 0
        value_2 = 0
        for each in self:
            if each.detailed_specification_ids:
                index = 0
                for line in each.detailed_specification_ids:
                    index+=1
                    if line.display_type == 'line_section':
                        if index > 2:
                            each.detailed_specification_ids[index-2].is_sum_line = True
                        value1 = 0
                    elif line.display_type == 'line_note':
                        value1 = 0
                        value_2 = 0
                        if index > 2:
                            each.detailed_specification_ids[index-2].is_sum_line = True
                            each.detailed_specification_ids[index-2].is_note_line = True
                    else:
                        value1 += line.amount * line.qty
                        value_2 += line.amount * line.qty
                    line.update({'section_sum' : value1})
                    line.update({'note_sum' : value_2})
                    each.vas_temp_amount = True
                each.detailed_specification_ids[-1].is_sum_line = True
                each.detailed_specification_ids[-1].is_note_line = True
            else:
                each.vas_temp_amount = False

    @api.depends('type')
    def _compute_is_amc(self):
        for record in self:
            if record.type == 'amc':
                record.is_amc = True
            else:
                record.is_amc = False    

    def create_revision(self):
        self.ensure_one()
        if not self.is_amc:
            number = self.revision_number + 1
            if self.is_revision == True:
                name = self.original_sale_order_id.name+f"/R0{number}"
            else:
                name = self.name+f"/R0{number}"
     
            new_sale_order = self.copy({
                
                'name':name,
                'revision_number': self.revision_number + 1,
                'original_sale_order_id': self.original_sale_order_id.id if self.original_sale_order_id else self.id,
                'is_revision': True,
                'pool_functionality':self.pool_functionality if self.pool_functionality else False,

                # 'pool_specification_ids':self.pool_specification_ids if self.pool_specification_ids else False,
                # 'pool_dimension_ids':self.pool_dimension_ids if self.pool_dimension_ids else False,
                # 'pricing_structure_ids':self.pricing_structure_ids if self.pricing_structure_ids else False,
                # 'mep_equipment_ids':self.mep_equipment_ids if self.mep_equipment_ids else False,
                'signed_by':self.signed_by if self.signed_by else False,
                'signed_on':self.signed_on if self.signed_on else False,
                'signature':self.signature if self.signature else False,
                'state':'draft',
                'is_not_latest_revision': False
            })
            new_sale_order.update({'name':name})
            new_sale_order.write({'is_revise': False})
            self.is_not_latest_revision = True
            
            if self.pool_specification_ids:
                pool_specification = []                                              
                for pool_spec in self.pool_specification_ids:
                    pool_specification.append((0, 0, {
                        'pool_specification_sl_no': pool_spec.pool_specification_sl_no,
                        'area_of_pool': pool_spec.area_of_pool,
                        'location_of_pool': pool_spec.location_of_pool,
                        'pool_loc': pool_spec.pool_loc,
                        'volume_of_water': pool_spec.volume_of_water,
                        'pool_filteration_system': pool_spec.pool_filteration_system,
                        'filteration_system': pool_spec.filteration_system,
                        'auto_dozing_system': pool_spec.auto_dozing_system,
                        'disinfection_system': pool_spec.disinfection_system,
                        'pool_finishing_type': pool_spec.pool_finishing_type,
                        'age_of_pool': pool_spec.age_of_pool,
                        'distance_from_camp': pool_spec.distance_from_camp,
                        'distance_from_other_pools': pool_spec.distance_from_other_pools,
                        'pools_in_circuit': pool_spec.pools_in_circuit,
                        'visit_frequency': pool_spec.visit_frequency,
                        'visit_type':pool_spec.visit_type,
                        'sub_visit_type': pool_spec.sub_visit_type,
                        'accomodation':pool_spec.accomodation,
                    }))
                new_sale_order.pool_specification_ids = pool_specification
                
            if self.vas_exclusions:
                vas_exclusions = []
                for vas_ex in self.vas_exclusions:    
                    vas_exclusions.append((0, 0, {
                        'description':vas_ex.description,
                    }))
                new_sale_order.vas_exclusions = vas_exclusions
                
            if self.vas_warranty_details:
                vas_warranty_details = []
                for vas_warranty in self.vas_warranty_details:    
                    vas_warranty_details.append((0, 0, {
                        'description':vas_warranty.description,
                    }))
                new_sale_order.vas_warranty_details = vas_warranty_details
                
            if self.warranty_exclusions_ids:
                warranty_exclusions_ids = []
                for vas_warranty_exc in self.warranty_exclusions_ids:    
                    warranty_exclusions_ids.append((0, 0, {
                        'description':vas_warranty_exc.description,
                    }))
                new_sale_order.warranty_exclusions_ids = warranty_exclusions_ids 
                
            if self.delivery_period_ids:
                delivery_period_ids = []
                for delivery_period in self.delivery_period_ids:    
                    delivery_period_ids.append((0, 0, {
                        'description':delivery_period.description,
                    }))
                new_sale_order.delivery_period_ids = delivery_period_ids 
                
            if self.payment_term_ids:
                payment_term_ids = []
                for payment_term in self.payment_term_ids:    
                    payment_term_ids.append((0, 0, {
                        'payment_term_id':payment_term.payment_term_id.id,
                    }))
                new_sale_order.payment_term_ids = payment_term_ids           
                          
            if self.pool_dimension_ids:
                pool_dimension = []                                              
                for pool_dim in self.pool_dimension_ids:
                    pool_dimension.append((0, 0, {
                        'pool_dimension_sl_no': pool_dim.pool_dimension_sl_no,
                        'length': pool_dim.length,
                        'breadth': pool_dim.breadth,
                        'pool_depth': pool_dim.pool_depth,
                        'water_depth': pool_dim.water_depth,
                        'water_volume': pool_dim.water_volume,
                        'pool_surface_area': pool_dim.pool_surface_area,
                        'coping_width': pool_dim.coping_width,
                        'coping_surface_area': pool_dim.coping_surface_area,
                        'total_surface_area': pool_dim.total_surface_area,
                    
                    }))
                new_sale_order.pool_dimension_ids = pool_dimension
                
            if self.pricing_structure_ids:
                pricing_structure = []                                              
                for  pricing_struct in self.pricing_structure_ids:
                    pricing_structure.append((0, 0, {
                        'display_type': pricing_struct.display_type,
                        'name': pricing_struct.name,
                        'pool_structure_sl_no': pricing_struct.pool_structure_sl_no,
                        'is_manpower': pricing_struct.is_manpower,
                        'is_consumables': pricing_struct.is_consumables,
                        'is_toolsequipment': pricing_struct.is_toolsequipment,
                        'is_sum_line': pricing_struct.is_sum_line,
                        'item_master_id': pricing_struct.item_master_id,
                        'out_of': pricing_struct.out_of,
                        'description': pricing_struct.description,
                        'unit': pricing_struct.unit,
                        'boq': pricing_struct.boq,
                        'unit_rate': pricing_struct.unit_rate,
                        'amount': pricing_struct.amount,
                        'total_amount': pricing_struct.total_amount,
                        'remarks': pricing_struct.remarks,
                    }))
                    
                new_sale_order.pricing_structure_ids = pricing_structure
                
            if self.mep_equipment_ids:
                mep_equipment = []                                              
                for   mep_equip in self.mep_equipment_ids:
                    mep_equipment.append((0, 0, {
                        'equipment_id': mep_equip.equipment_id.id,
                        'equipment_make': mep_equip.equipment_make,
                        'equipment_qty': mep_equip.equipment_qty,
                        'equipment_type': mep_equip.equipment_type,
                        'equipment_size': mep_equip.equipment_size,
                      
                    }))

                new_sale_order.mep_equipment_ids = mep_equipment
            new_revision = self.env['sale.revision'].create({
                        'sale_order_id': self.id, 
                        'sale_order_history_id': new_sale_order.id,
                    })
            if self.revision_number >= 1 and self.original_sale_order_id:
                revision = self.env['sale.revision'].create({
                        'sale_order_id':self.original_sale_order_id.id, 
                        'sale_order_history_id': new_sale_order.id,
                    })
            revision_list = []
            revision_list.append((0, 0, {
                                'sale_order_id': self.id, 
                                'sale_order_history_id': self.id,
            }))
            new_sale_order.sale_revision_ids = revision_list


            # self.sale_revision_ids.sale_order_history_id = self.id
            self.state = 'revise'
            self.write({'is_revise': False})
            new_sale_order.message_post(
                body=f"Sale order revised from {self.name}. New revision: {new_sale_order.revision_number}")
        else:
            # Handle AMC-specific revisions
            number = self.amc_revision_number + 1
            if self.is_revision == True:
                name = self.original_sale_order_id.name+f"/R0{number}"
            else:
                name = self.name+f"/R0{number}"
          
  
                
            new_sale_order = self.copy({
                'name':name,
                'amc_revision_number': self.amc_revision_number + 1,
                'revision_number': self.revision_number + 1,
                'original_sale_order_id': self.original_sale_order_id.id if self.original_sale_order_id else self.id,
                'is_revision': True,
                'is_amc': True,
                # 'pool_specification_ids': [(6, 0, [record.id for record in self.pool_specification_ids])] if self.pool_specification_ids else False,
                'pool_functionality':self.pool_functionality if self.pool_functionality else False,
                # 'pool_dimension_ids':self.pool_dimension_ids,
                # 'pricing_structure_ids':self.pricing_structure_ids,
                # 'mep_equipment_ids':self.mep_equipment_ids,
                'signed_by':self.signed_by if self.signed_by else False,
                'signed_on':self.signed_on if self.signed_on else False,
                'signature':self.signature if self.signature else False,
                'state':'draft',
                'is_not_latest_revision': False
                # Optionally, you can add logic to adjust AMC dates or other fields
            })
            new_sale_order.update({'name':name})
            new_sale_order.write({'is_revise': False})
            self.is_not_latest_revision = True

            if self.pool_specification_ids:
                pool_specification = []                                              
                for pool_spec in self.pool_specification_ids:
                    pool_specification.append((0, 0, {
                        'pool_specification_sl_no': pool_spec.pool_specification_sl_no,
                        'area_of_pool': pool_spec.area_of_pool,
                        'location_of_pool': pool_spec.location_of_pool,
                        'pool_loc': pool_spec.pool_loc,
                        'volume_of_water': pool_spec.volume_of_water,
                        'pool_filteration_system': pool_spec.pool_filteration_system,
                        'filteration_system': pool_spec.filteration_system,
                        'auto_dozing_system': pool_spec.auto_dozing_system,
                        'disinfection_system': pool_spec.disinfection_system,
                        'pool_finishing_type': pool_spec.pool_finishing_type,
                        'age_of_pool': pool_spec.age_of_pool,
                        'distance_from_camp': pool_spec.distance_from_camp,
                        'distance_from_other_pools': pool_spec.distance_from_other_pools,
                        'pools_in_circuit': pool_spec.pools_in_circuit,
                        'visit_frequency': pool_spec.visit_frequency,
                        'visit_type':pool_spec.visit_type,
                        'sub_visit_type': pool_spec.sub_visit_type,
                        'accomodation':pool_spec.accomodation,
                    }))
                new_sale_order.pool_specification_ids = pool_specification
    
            if self.pool_dimension_ids:
                pool_dimension = []                                              
                for pool_dim in self.pool_dimension_ids:
                    pool_dimension.append((0, 0, {
                        'pool_dimension_sl_no': pool_dim.pool_dimension_sl_no,
                        'length': pool_dim.length,
                        'breadth': pool_dim.breadth,
                        'pool_depth': pool_dim.pool_depth,
                        'water_depth': pool_dim.water_depth,
                        'water_volume': pool_dim.water_volume,
                        'pool_surface_area': pool_dim.pool_surface_area,
                        'coping_width': pool_dim.coping_width,
                        'coping_surface_area': pool_dim.coping_surface_area,
                        'total_surface_area': pool_dim.total_surface_area,
                    
                    }))
                new_sale_order.pool_dimension_ids = pool_dimension
                
            if self.pricing_structure_ids:
                pricing_structure = []                                              
                for  pricing_struct in self.pricing_structure_ids:
                    pricing_structure.append((0, 0, {
                        'display_type': pricing_struct.display_type,
                        'name': pricing_struct.name,
                        'pool_structure_sl_no': pricing_struct.pool_structure_sl_no,
                        'is_manpower': pricing_struct.is_manpower,
                        'is_consumables': pricing_struct.is_consumables,
                        'is_toolsequipment': pricing_struct.is_toolsequipment,
                        'is_sum_line': pricing_struct.is_sum_line,
                        'item_master_id': pricing_struct.item_master_id,
                        'out_of': pricing_struct.out_of,
                        'description': pricing_struct.description,
                        'unit': pricing_struct.unit,
                        'boq': pricing_struct.boq,
                        'unit_rate': pricing_struct.unit_rate,
                        'amount': pricing_struct.amount,
                        'total_amount': pricing_struct.total_amount,
                        'remarks': pricing_struct.remarks,
                    }))
                    
                new_sale_order.pricing_structure_ids = pricing_structure
            new_sale_order   

                
            if self.mep_equipment_ids:
                mep_equipment = []                                              
                for   mep_equip in self.mep_equipment_ids:
                    mep_equipment.append((0, 0, {
                        'equipment_id': mep_equip.equipment_id.id,
                        'equipment_make': mep_equip.equipment_make,
                        'equipment_qty': mep_equip.equipment_qty,
                        'equipment_type': mep_equip.equipment_type,
                        'equipment_size': mep_equip.equipment_size,
                        'image':mep_equip.image,
                      
                    }))

                new_sale_order.mep_equipment_ids = mep_equipment
                    
    
                
            
            new_revision = self.env['sale.revision'].create({
                        'sale_order_id': self.id, 
                        'sale_order_history_id': new_sale_order.id,
                    })
            if self.revision_number >= 1 and self.original_sale_order_id:
                revision = self.env['sale.revision'].create({
                        'sale_order_id':self.original_sale_order_id.id, 
                        'sale_order_history_id': new_sale_order.id,
                    })
                
            if self.terms_condtion_corporate_ids:
                terms_condtion_corporate = []                                              
                for terms_condtion in self.terms_condtion_corporate_ids:
                    terms_condtion_corporate.append((0, 0, {
                        'description': terms_condtion.description,
                    }))

                new_sale_order.terms_condtion_corporate_ids = terms_condtion_corporate   

            if self.terms_conditions_ids:
                terms_conditions = []                                              
                for terms_condtion_non in self.terms_conditions_ids:
                    terms_conditions.append((0, 0, {
                        'description': terms_condtion_non.description,
                    }))

                new_sale_order.terms_conditions_ids = terms_conditions    
                
            if self.specific_conditions_corporate_ids:
                specific_conditions_corporate = []                                              
                for specific_conditions in self.specific_conditions_corporate_ids:
                    specific_conditions_corporate.append((0, 0, {
                        'description': specific_conditions.description,
                    }))

                new_sale_order.specific_conditions_corporate_ids = specific_conditions_corporate  

            if self.specific_conditions_ids:
                specific_conditions = []                                              
                for specific_conditions_non in self.specific_conditions_ids:
                    specific_conditions.append((0, 0, {
                        'description': specific_conditions_non.description,
                    }))

                new_sale_order.specific_conditions_ids = specific_conditions      



                
                
                
            if self.general_scope_corporate_ids:
                general_scope_corporate = []                                              
                for general_scope in self.general_scope_corporate_ids:
                    general_scope_corporate.append((0, 0, {
                        'description': general_scope.description,
                    }))

                new_sale_order.general_scope_corporate_ids = general_scope_corporate    

            if self.general_scope_ids:
                general_scope = []                                              
                for general_scope_non in self.general_scope_ids:
                    general_scope.append((0, 0, {
                        'description': general_scope_non.description,
                    }))

                new_sale_order.general_scope_ids = general_scope    
                
            
            if self.detailed_scope_corporate_ids:
                detailed_scope_corporate = []                                              
                for detailed_scope in self.detailed_scope_corporate_ids:
                    detailed_scope_corporate.append((0, 0, {
                        'description': detailed_scope.description,
                    }))

                new_sale_order.detailed_scope_corporate_ids = detailed_scope_corporate   

            
            if self.detailed_scope_ids:
                detailed_scope = []                                              
                for detailed_scope_non in self.detailed_scope_ids:
                    detailed_scope.append((0, 0, {
                        'description': detailed_scope_non.description,
                    }))

                new_sale_order.detailed_scope_ids = detailed_scope    
                
                
            if self.amc_scope_corporate_ids:
                amc_scope_corporate = []                                              
                for amc_scope in self.amc_scope_corporate_ids:
                    amc_scope_corporate.append((0, 0, {
                        'description': amc_scope.description,
                    }))

                new_sale_order.amc_scope_corporate_ids = amc_scope_corporate

            if self.amc_scope_ids:
                amc_scope = []                                              
                for amc_scope_non in self.amc_scope_ids:
                    amc_scope.append((0, 0, {
                        'description': amc_scope_non.description,
                    }))

                new_sale_order.amc_scope_ids = amc_scope    
                
            if self.amc_asset_details:
                amc_asset_details_list = []                                              
                for amc_asset in self.amc_asset_details:
                    amc_asset_details_list.append((0, 0, {
                        'sl_no': amc_asset.sl_no,
                        'name': amc_asset.name,
                        'asset_action': amc_asset.asset_action,
                    }))

                new_sale_order.amc_asset_details = amc_asset_details_list     
                
            if self.sale_chemical_use_line_ids:
                sale_chemical_use = []                                              
                for sale_chemical in self.sale_chemical_use_line_ids:
                    sale_chemical_use.append((0, 0, {
                        'name': sale_chemical.name,
                        'pool_structure_sl_no': sale_chemical.pool_structure_sl_no,
                    }))

                new_sale_order.sale_chemical_use_line_ids = sale_chemical_use      
                
                
            if self.sale_manpower_line_ids:
                sale_manpower_line = []                                              
                for sale_manpower in self.sale_manpower_line_ids:
                    sale_manpower_line.append((0, 0, {
                        'name': sale_manpower.name,
                        'pool_structure_sl_no': sale_manpower.pool_structure_sl_no,
                    }))
                new_sale_order.sale_manpower_line_ids = sale_manpower_line    
                

            self.state = 'revise'
            self.write({'is_revise': False})    
            new_sale_order.message_post(
                body=f"AMC Sale order revised from {self.name}. New AMC revision: {new_sale_order.amc_revision_number}")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order Revision',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': new_sale_order.id,
            'target': 'current',
        }

    @api.depends('project_ids')
    def _compute_project_count(self):
        for order in self:
            order.project_count = len(order.project_ids)



    def write(self, vals):
        res = super().write(vals)
        if 'type' in vals:
            weekly_plan_id = self.env['sale.subscription.plan'].search([('is_weekly','=',True)]).id
            monthly_plan_id = self.env['sale.subscription.plan'].search([('is_monthly','=',True)]).id
            yearly_plan_id = self.env['sale.subscription.plan'].search([('is_yearly','=',True)]).id
            for each in self.pool_specification_ids:
                if 1 == each.pool_specification_sl_no:
                    if each.visit_type and each.visit_type == 'monthly':
                        self.plan_id = monthly_plan_id
                        self.visit_freq = each.visit_frequency
                    if each.visit_type and each.visit_type == 'yearly':
                        self.plan_id = yearly_plan_id
                        self.visit_freq = each.visit_frequency
                    if each.visit_type and each.visit_type == 'weekly':
                        self.plan_id = weekly_plan_id
                        self.visit_freq = each.visit_frequency
            num_of_pools = self.no_of_pools
            lines = []
            if self.order_line:
                for line in self.order_line:
                    lines.append(line.id)
            # for i in range(2,num_of_pools+1):
            #     for each in self.pool_specification_ids:
            #         if i == each.pool_specification_sl_no:
            #             if each.visit_type and each.visit_type == 'monthly':
            #                 self.env['sale.order'].sudo().create({
            #                     'partner_id':self.partner_id.id,
            #                     'type':self.type,
            #                     'visit_freq':each.visit_frequency,
            #                     'plan_id':monthly_plan_id,
            #                     'order_line' : lines if self.order_line else False
            #                 })
            #             if each.visit_type and each.visit_type == 'yearly':
            #                 self.env['sale.order'].sudo().create({
            #                     'partner_id':self.partner_id.id,
            #                     'type':self.type,
            #                     'visit_freq':each.visit_frequency,
            #                     'plan_id':yearly_plan_id,
            #                     'order_line' : lines if self.order_line else False
            #                 }) 
            #             if each.visit_type and each.visit_type == 'weekly':
            #                 self.env['sale.order'].sudo().create({
            #                     'partner_id':self.partner_id.id,
            #                     'type':self.type,
            #                     'visit_freq':each.visit_frequency,
            #                     'plan_id':weekly_plan_id,
            #                     'order_line' : lines if self.order_line else False
            #                 }) 
        return res
    



    
    @api.model_create_multi
    def create(self, vals_list):
        sales = super(SaleOrder, self).create(vals_list)
        weekly_plan_id = self.env['sale.subscription.plan'].search([('is_weekly','=',True)]).id
        monthly_plan_id = self.env['sale.subscription.plan'].search([('is_monthly','=',True)]).id
        yearly_plan_id = self.env['sale.subscription.plan'].search([('is_yearly','=',True)]).id
        for sale in sales:
            if sale.type in ['amc']:
                for each in sale.pool_specification_ids:
                    if 1 == each.pool_specification_sl_no:
                        if each.visit_type and each.visit_type == 'monthly':
                            sale.plan_id = monthly_plan_id
                            sale.visit_freq = each.visit_frequency
                        if each.visit_type and each.visit_type == 'yearly':
                            sale.plan_id = yearly_plan_id
                            sale.visit_freq = each.visit_frequency
                        if each.visit_type and each.visit_type == 'weekly':
                            sale.plan_id = weekly_plan_id
                            sale.visit_freq = each.visit_frequency
                if sale.order_line:
                    lines = []
                    for line in sale.order_line:
                        lines.append((0, 0, {
                            'product_template_id': line.product_template_id.id,
                            'product_id': line.product_id.id,
                            'product_uom_qty': line.product_uom_qty,
                            'product_uom':line.product_uom.id,
                            'price_unit':line.price_unit,
                            'name':line.name
                    }))
                num_of_pools = sale.no_of_pools
                # for i in range(2,num_of_pools+1):
                # if sale.pool_specification_ids:
                #     for each in sale.pool_specification_ids:
                #         if each.pool_specification_sl_no:
                #             if each.visit_type and each.visit_type == 'monthly':
                #                 self.env['sale.order'].sudo().create({
                #                     'partner_id':sale.partner_id.id,
                #                     'type':sale.type,
                #                     'visit_freq':each.visit_frequency,
                #                     'plan_id':monthly_plan_id,
                #                     'order_line' : lines if sale.order_line else False
                #                 })
                #             if each.visit_type and each.visit_type == 'yearly':
                #                 self.env['sale.order'].sudo().create({
                #                     'partner_id':sale.partner_id.id,
                #                     'type':sale.type,
                #                     'visit_freq':each.visit_frequency,
                #                     'plan_id':yearly_plan_id,
                #                     'order_line' : lines if sale.order_line else False
                #                 }) 
                #             if each.visit_type and each.visit_type == 'weekly':
                #                 self.env['sale.order'].sudo().create({
                #                     'partner_id':sale.partner_id.id,
                #                     'type':sale.type,
                #                     'visit_freq':each.visit_frequency,
                #                     'plan_id':weekly_plan_id,
                #                     'order_line' : lines if sale.order_line else False
                #                 }) 
        return sales


    def custom_confirm_button(self):
        pass
        # self.action_confirm()
        # sale_order = self.id
        # if self.type == 'amc':
        #     if not self.plan_id:
        #         raise ValidationError(_('Please mention Invoicing Frequency!!'))
            
        # if self.type in ['vas']:
        #     self.action_confirm()
        #     project = self.env['project.project'].create({
        #         'name': f'Project for Sale Order {self.name}',
        #         'partner_id': self.partner_id.id,
        #         'order_id': sale_order,
        #         'user_id': self.env.user.id,
        #     })
        #     for line in self.order_line:
        #         if line.product_id:
        #             self.env['project.task'].create({
        #                 'name': line.product_id.name,
        #                 'project_id': project.id,
        #                 'sale_line_id': line.id,
        #                 'partner_id': self.partner_id.id,
        #             })
        #     self.project_ids = [(4, project.id)]

        #     return {
        #         'type': 'ir.actions.act_window',
        #         'name': 'Project',
        #         'res_model': 'project.project',
        #         'view_mode': 'form',
        #         'res_id': project.id,
        #         'target': 'current',
        #         'view_id': False,
        #         'context': {
        #             'default_name': f'Project for Sale Order {self.name}',
        #             'default_user_id': self.env.user.id,
        #             'default_sale_order_id': self.id,
        #             'default_partner_id': self.partner_id.id,
        #         },
        #     }
        # elif self.type in ['amc']:
        #     self.action_confirm()
        #     num_of_pools = self.no_of_pools
        #     if num_of_pools:
        #         weekly_plan_id = self.env['sale.subscription.plan'].search([('is_weekly','=',True)]).id
        #         monthly_plan_id = self.env['sale.subscription.plan'].search([('is_monthly','=',True)]).id
        #         yearly_plan_id = self.env['sale.subscription.plan'].search([('is_yearly','=',True)]).id
        #         lines = []
        #         if self.order_line:
        #             for line in self.order_line:
        #                 lines.append(line.id)

        #         for i in range(2,num_of_pools+1):
        #             for each in self.pool_specification_ids:
        #                 if i == each.pool_specification_sl_no:
        #                     if each.visit_type and each.visit_type == 'monthly':
        #                         self.env['sale.order'].sudo().create({
        #                             'partner_id':self.partner_id.id,
        #                             'type':self.type,
        #                             'visit_freq':each.visit_frequency,
        #                             'plan_id':monthly_plan_id,
        #                             'order_line' : lines if lines else False
        #                         })
        #                     if each.visit_type and each.visit_type == 'yearly':
        #                         self.env['sale.order'].sudo().create({
        #                             'partner_id':self.partner_id.id,
        #                             'type':self.type,
        #                             'visit_freq':each.visit_frequency,
        #                             'plan_id':yearly_plan_id,
        #                             'order_line' : lines if lines else False
        #                         }) 
        #                     if each.visit_type and each.visit_type == 'weekly':
        #                         self.env['sale.order'].sudo().create({
        #                             'partner_id':self.partner_id.id,
        #                             'type':self.type,
        #                             'visit_freq':each.visit_frequency,
        #                             'plan_id':weekly_plan_id,
        #                             'order_line' : lines if lines else False
        #                         }) 
            # return {
            #     'name': 'Annual Maintenance Contract',
            #     'view_mode': 'form',
            #     'res_model': 'amc.plan',
            #     'type': 'ir.actions.act_window',
            #     'target': 'new',
            #     'context': {'default_customer_id': self.partner_id.id,
            #                 'default_sale_order_id' : self.id,
            #                 'default_services_involved' : self.order_line.product_template_id.ids,
            #     }
            # }

    def action_view_projects(self):
        return {
            'name': 'Projects',
            'view_mode': 'list,form',
            'res_model': 'project.project',
            'type': 'ir.actions.act_window',
            'domain': [('order_id', '=', self.id)],
            'context': self.env.context,
        }

    def action_amc_view(self):
        return {
            'name': 'Annual Maintenance Contract',
            'view_mode': 'list,form',
            'res_model': 'amc.plan',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': f'[("sale_order_id","=", {self.id})]',
        }

    @api.model
    def _compute_get_amc(self):
        for rec in self:
            records = self.env["amc.plan"].search([("sale_order_id", "=", rec.id)])
            rec.amc_count = len(records)

    def action_cron_auto_field_service(self):
        weekly_plan_id = self.env['sale.subscription.plan'].search([('is_weekly','=',True)]).id
        monthly_plan_id = self.env['sale.subscription.plan'].search([('is_monthly','=',True)]).id
        yearly_plan_id = self.env['sale.subscription.plan'].search([('is_yearly','=',True)]).id
        project_id = self.env['project.project'].search([('is_field_service','=',True)])
        current_month = fields.Date.today().month
        sale_sub_ids = self.env['sale.order'].search([('is_subscription','=',True),('state','=', 'sale')])
        for each_rec in sale_sub_ids:
            sale_line_name_parts = each_rec.order_line[0].name.split('\n')
            title = sale_line_name_parts[0] or each_rec.order_line[0].product_id.name
            if each_rec.next_invoice_date <= each_rec.end_date:
                nxt_inv_date = each_rec.next_invoice_date
                if each_rec.plan_id.id == monthly_plan_id:  ######Monthly
                    task_create_date = nxt_inv_date -relativedelta(days = 1)
                    if task_create_date == fields.Date.today():
                        for i in range(0,int(each_rec.visit_freq)):
                            allocated_hours = 0.0
                            task_vals = {
                                'name': '%s - %s' % (each_rec.name or '', title) if each_rec.order_line else title,
                                'allocated_hours': allocated_hours,
                                'partner_id': each_rec.partner_id.id if each_rec.partner_id else False,
                                'project_id': project_id.id,
                                'sale_line_id':each_rec.order_line[0].id if each_rec.order_line else False,
                                'sale_order_id': each_rec.id,
                                'company_id': project_id.company_id.id if each_rec.company_id else False,
                                'user_ids': False,  
                            }
                            self.env['project.task'].sudo().create(task_vals)
                
                elif each_rec.plan_id.id == weekly_plan_id:   ######weekly
                    if each_rec.date_order.date() != nxt_inv_date:
                        week_date = nxt_inv_date-relativedelta(days = 1)
                        if week_date == fields.Date.today():
                            for i in range(0,int(each_rec.visit_freq)):
                                    allocated_hours = 0.0
                                    task_vals = {
                                        'name': '%s - %s' % (each_rec.name or '', title) if each_rec.order_line else title,
                                        'allocated_hours': allocated_hours,
                                        'partner_id': each_rec.partner_id.id if each_rec.partner_id else False,
                                        'project_id': project_id.id,
                                        'sale_line_id':each_rec.order_line[0].id if each_rec.order_line else False,
                                        'sale_order_id': each_rec.id,
                                        'company_id': project_id.company_id.id if each_rec.company_id else False,
                                        'user_ids': False,  
                                    }
                                    self.env['project.task'].sudo().create(task_vals)

                elif each_rec.plan_id.id == yearly_plan_id:  #####Yearly
                    current_year = fields.Date.today().year
                    if each_rec.next_invoice_date.year == current_year:
                            for i in range(0,int(each_rec.visit_freq)):
                                allocated_hours = 0.0
                                task_vals = {
                                    'name': '%s - %s' % (each_rec.name or '', title) if each_rec.order_line else title,
                                    'allocated_hours': allocated_hours,
                                    'partner_id': each_rec.partner_id.id if each_rec.partner_id else False,
                                    'project_id': project_id.id,
                                    'sale_line_id':each_rec.order_line[0].id if each_rec.order_line else False,
                                    'sale_order_id': each_rec.id,
                                    'company_id': project_id.company_id.id if each_rec.company_id else False,
                                    'user_ids': False,  # force non assigned task, as created as sudo()
                                }
                                self.env['project.task'].sudo().create(task_vals)

    def action_cancel(self):
        res = super().action_cancel()
        if self.is_revise == True:
            self.is_revise = False
        return res

    def action_confirm(self):
        res = super().action_confirm()
        if self.type == 'amc':
            if not (self.env.user.has_groups('bi_vas_amc.group_amc_confirm') or  self.env.user.has_groups('bi_vas_amc.group_vas_amc_confirm')):
                raise UserError("you don't have permission to confirm the order. Contact the Manager")
            if not self.plan_id:
                raise ValidationError(_('Please mention Invoicing Frequency!!'))
            if not self.end_date:
                raise ValidationError(_('Please mention end date..'))
        if self.is_subscription:
            if self.pool_specification_ids:
                if not self.end_date or not self.pool_specification_ids[0].visit_frequency:
                    raise ValidationError(_('Please mention End Date and Visit Frequency!!'))
            if not self.team_lead_id and not self.technician_ids:
                raise ValidationError(_('Please mention Team Lead and Technicians...'))
            if not self.m_number:
                raise ValidationError(_('Please provide M-Number...!'))
            weekly_plan_id = self.env['sale.subscription.plan'].search([('is_weekly','=',True)]).id
            monthly_plan_id = self.env['sale.subscription.plan'].search([('is_monthly','=',True)]).id
            yearly_plan_id = self.env['sale.subscription.plan'].search([('is_yearly','=',True)]).id
            project_id = self.env['project.project'].search([('is_field_service','=',True)])
            current_month = fields.Date.today().month
            # sale_sub_ids = self.env['sale.order'].search([('is_subscription','=',True),('state','=', 'sale')])
            sale_line_name_parts = self.order_line[0].name.split('\n')
            title = sale_line_name_parts[0] or self.order_line[0].product_id.name
            # if self.next_invoice_date <= self.end_date:
            usr_list = []
            if self.team_lead_id and self.team_lead_id.user_id:
                usr_list.append(self.team_lead_id.user_id.id)
            # nxt_inv_date = self.next_invoice_date
            if self.plan_id.id == monthly_plan_id:  ######Monthly
                for i in range(0,int(self.visit_freq)):
                    allocated_hours = 0.0
                    task_vals = {
                        'name': '%s - %s' % (self.name or '', title) if self.order_line else title,
                        'allocated_hours': allocated_hours,
                        'partner_id': self.partner_id.id if self.partner_id else False,
                        'project_id': project_id.id,
                        'sale_line_id':self.order_line[0].id if self.order_line else False,
                        'user_ids':usr_list,
                        'sale_order_id': self.id,
                        'company_id': project_id.company_id.id if self.company_id else False,
                    }
                    self.env['project.task'].sudo().create(task_vals)
            
            elif self.plan_id.id == weekly_plan_id:   ######weekly
                for i in range(0,int(self.visit_freq)):
                        allocated_hours = 0.0
                        task_vals = {
                            'name': '%s - %s' % (self.name or '', title) if self.order_line else title,
                            'allocated_hours': allocated_hours,
                            'partner_id': self.partner_id.id if self.partner_id else False,
                            'project_id': project_id.id,
                            'sale_line_id':self.order_line[0].id if self.order_line else False,
                            'user_ids':usr_list,
                            'sale_order_id': self.id,
                            'company_id': project_id.company_id.id if self.company_id else False,
                        }
                        self.env['project.task'].sudo().create(task_vals)

            elif self.plan_id.id == yearly_plan_id:  #####Yearly
                for i in range(0,int(self.visit_freq)):
                    allocated_hours = 0.0
                    task_vals = {
                        'name': '%s - %s' % (self.name or '', title) if self.order_line else title,
                        'allocated_hours': allocated_hours,
                        'partner_id': self.partner_id.id if self.partner_id else False,
                        'project_id': project_id.id,
                        'sale_line_id':self.order_line[0].id if self.order_line else False,
                        'user_ids':usr_list,
                        'sale_order_id': self.id,
                        'company_id': project_id.company_id.id if self.company_id else False,
                    }
                    self.env['project.task'].sudo().create(task_vals)

        if self.type == 'vas':
            if not (self.env.user.has_groups('bi_vas_amc.group_vas_confirm') or self.env.user.has_groups('bi_vas_amc.group_vas_amc_confirm')):
                raise UserError("you don't have permission to confirm the order. Contact the Manager")
            
        
        sale_order = self.id
        project = self.env['project.project'].create({
                'name': f'Project for Sale Order {self.name}',
                'partner_id': self.partner_id.id,
                'order_id': sale_order,
                'user_id': self.env.user.id,
                'company_id': self.company_id.id
            })
        self.project_ids = [(4, project.id)]
        self.order_line.distribution_analytic_account_ids = [(4, project.account_id.id)]
        self.write({'is_revise': False})
        return res

        # for line in self.order_line:
        #     if line.product_id:
        #         self.env['project.task'].create({
        #             'name': line.product_id.name,
        #             'project_id': project.id,
        #             'sale_line_id': line.id,
        #             'partner_id': self.partner_id.id,
        #         })
        

            # return {
            #     'type': 'ir.actions.act_window',
            #     'name': 'Project',
            #     'res_model': 'project.project',
            #     'view_mode': 'form',
            #     'res_id': project.id,
            #     'target': 'current',
            #     'view_id': False,
            #     'context': {
            #         'default_name': f'Project for Sale Order {self.name}',
            #         'default_user_id': self.env.user.id,
            #         'default_sale_order_id': self.id,
            #         'default_partner_id': self.partner_id.id,
            #     },
            # }

    def update_analytic_account(self):
        project_id = self.env['project.project'].search([('order_id', '=', self.id)])
        analytic_account_id = project_id.account_id
        if project_id:
            for rec in self:
                for inv in rec.invoice_ids:
                    for line in inv.invoice_line_ids:
                        if rec.type == 'amc':
                            line.analytic_distribution =  {str(analytic_account_id.id): 100}
                        if rec.type == 'vas':
                            line.analytic_distribution =  {str(analytic_account_id.id): 100}


        
    def create_project(self):
        sale_order = self.id
        project = self.env['project.project'].create({
                'name': f'Project for Sale Order {self.name}',
                'partner_id': self.partner_id.id,
                'order_id': sale_order,
                'user_id': self.env.user.id,
                'company_id': self.company_id.id
            })
        self.project_ids = [(4, project.id)]
        

    def action_submits(self):
        for rec in self:
            self.state = 'submitted'
            self.write({'is_revise': False})
        
            group_vas_head = self.env.ref('bi_vas_amc.group_vas_confirm')
            group_amc_head = self.env.ref('bi_vas_amc.group_amc_confirm')
            group_vas_amc_head = self.env.ref('bi_vas_amc.group_vas_amc_confirm')

            if rec.type == 'vas':
                target_group = [group_vas_head.id, group_vas_amc_head.id]
            else:  
                target_group = [group_amc_head.id, group_vas_amc_head.id]

            users = self.env["res.users"].search([("groups_id", "in", target_group)])
            activity_type_id = self.env.ref('mail.mail_activity_data_todo').id
            model = self.env["ir.model"].sudo().search([("model", "=", "sale.order")])

            for user in users:
                activity_vals = {
                    'activity_type_id': activity_type_id,
                    'user_id': user.id,
                    'res_id': rec.id,
                    'res_model_id': model.id,
                    'note': f'Sale Order ({rec.name}) of type {rec.type} has been submitted.',
                }
                self.env['mail.activity'].sudo().create(activity_vals)

    def _confirmation_error_message(self):
        """ Return whether order can be confirmed or not if not then returm error message. """
        self.ensure_one()
        if self.state not in {'sent', 'waiting', 'approved'}:
            return _("Some orders are not in a state requiring confirmation.")
        if any(
            not line.display_type
            and not line.is_downpayment
            and not line.product_id
            for line in self.order_line
        ):
            return _("A line on these orders missing a product, you cannot confirm it.")

        return False
    
    
    @api.onchange('plan_id')
    def _onchange_plan_id(self):
        if self.plan_id.uom_id:
            uom_id = self.plan_id.uom_id
            for line in self.order_line:
                if line and line.product_uom:
                    line.product_uom = uom_id

    # @api.onchange('vas_job_number')
    # def _onchange_plan_id(self):
    #     for rec in self:
    #         job_number = rec.original_sale_order_id.vas_job_number
    #         if rec.vas_job_number.id != job_number.id:
    #             raise UserError("Does't Match The Parent Sale order AMC Job-Number")
                

class RevisionHistory(models.Model):
    _name = 'sale.revision' 
    _description = "Revision History" 
    
    sale_order_id = fields.Many2one('sale.order', string = "Sale Order")  
    
    sale_order_history_id = fields.Many2one('sale.order', string = "Revision's")




class PaymentTermVas(models.Model):
    _name = 'payment.term.vas'
    _description = 'Payment term Vas'


    description = fields.Char("Description")
    sale_id = fields.Many2one('sale.order', string="Sale Order")

class ScopeofWork(models.Model):
    _name = 'scope.of.work.page'
    _description = 'Scope of Work'

    sale_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")
    

class DetailedSpecification(models.Model):
    _name = 'detailed.specification'
    _description = 'Detailed Specification'

    sale_id = fields.Many2one('sale.order', string="Sale Order")
    name = fields.Char(string="Name")
    # detailed_specification = fields.Many2one(
    #     'detailed.specification.master',  # The target model
    #     string="Description",
    # )
    description_note = fields.Text(string="Main Section")

    item = fields.Char(string="Description")
    display_type = fields.Selection(
        selection=[
            ('line_section', "Section"),
            ('line_note', "Note"),
            ('line_item', "Item")
        ],
        default=False,
        store=True
    )
    qty = fields.Float(string='Qty')
    uom_id = fields.Many2one('uom.uom', string="Unit")
    tax_id = fields.Many2one('account.tax', string="Vat")
    amount = fields.Float(string="Amount", digits=(16,3))
    total_amount = fields.Float(string="Total", digits=(16,3))
    discount = fields.Float(string="Discount")
    section_sum = fields.Float(string="Section Sum", digits=(16,3))
    note_sum = fields.Float(string="Note Sum", digits=(16,3))
    is_sum_line = fields.Boolean('Is Sum')
    is_note_line = fields.Boolean('Is Note')

    @api.onchange('qty','amount','discount')
    def _onchange_qty_amnt(self):
        for rec in self:
            # if rec.sale_id.type == 'vas':
            if rec.discount:
                rec.total_amount = (rec.qty * rec.amount)- rec.discount
            else:
                rec.total_amount = (rec.qty * rec.amount)

class ClientExclusions(models.Model):
    _name = 'client.exclusion'
    _description = 'Exclusions'
    _rec_name = 'description'

    # sale_id = fields.Many2one('sale.order', string="Sale Order")

    description = fields.Text(string="Description")
    active = fields.Boolean(default=True)
    
class ClientExclusionLine(models.Model):
    _name ='client.exclusion.line'
    _description = 'Exclusion Line'

    sale_id = fields.Many2one('sale.order', string="Sale Order")
    exclusion_id = fields.Many2one('client.exclusion', string='Description')



class VasWarrantyExclusion(models.Model):
    _name = 'vas.warranty.exclusion'
    _description = 'Warranty Exclusion'
    _rec_name = "description"

    description = fields.Char(string='Description', required=True)
    active = fields.Boolean(default=True)
    
class WarrantyDetails(models.Model):
    _name = 'warranty.details'
    _description = 'Warranty Details'
    _rec_name = 'description'

    # sale_id = fields.Many2one('sale.order', string="Sale Order")
    active = fields.Boolean(default=True)
  
    warranty_lines = fields.One2many('warranty.details.line', 'warranty_id', string="Warranty Lines")

    description = fields.Char(string="Description")
   
    
class WarrantyDetailsLine(models.Model):
    _name = 'warranty.details.line'
    _description = 'Warranty Details Line'

    name = fields.Char(string='Name',store=True)
    sale_id = fields.Many2one('sale.order', string="Sale Order")
    warranty_ids = fields.Many2one('warranty.details', string='Warranty Details', ondelete='cascade')

    warranty_id = fields.Many2one('warranty.details', string='Description')
    display_type = fields.Selection(
    selection=[
        ('line_section', "Section"),
    ],
    default=False,store=True)
    # description =  fields.Char(string="Description")

class WarrantyVasExclusion(models.Model):
    _name='warranty.vas.exclusion'
    _description = 'Vas Warranty Exclusion'

    name = fields.Char(string='Name',store=True)
    

    description = fields.Char(string="Description")

    vas_warranty_id = fields.One2many('vas.warranty.exclusion.line', 'vas_warranty_id', string="")
    sale_id = fields.Many2one('sale.order', string="Sale Order")


class VasWarrantyExclusionLine(models.Model):
    _name='vas.warranty.exclusion.line'
    _description ='Vas Warranty Exclusion Line'

    name = fields.Char(string='Name',store=True)
    vas_warranty_id = fields.Many2one('warranty.vas.exclusion')
    sale_id = fields.Many2one('sale.order', string="Sale Order")

class DetailedSpecificationMaster(models.Model):
    _name = 'detailed.specification.master'
    _description = 'Detailed Specification'
    _rec_name = 'description'

    description = fields.Text(string="Description")
    specification_line_ids = fields.One2many(
        comodel_name='specification.line',
        inverse_name='specification_id',
        string='Specification Lines'
    )
    active = fields.Boolean(default=True)

class SpecificationLine(models.Model):
    _name = 'specification.line'
    _description = 'Specification Line'


    name = fields.Char(string='Name')

    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note',"Note"),
        ('line_item', "Item"),
    ], string="Display Type")

    specification_id = fields.Many2one(
        comodel_name='detailed.specification.master',
        string='Specification Master'
    )
    item = fields.Char(string='Description')

    qty = fields.Float(string='Qty',default=1.00)
    uom_id = fields.Many2one('uom.uom', string="Unit")
    tax_id = fields.Many2one('account.tax', string="VAT")
    amount = fields.Float(string="Amount")

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_ids = fields.Binary(compute="_compute_product_ids",string="Compute product")

    @api.depends('order_id.type')
    def _compute_product_ids(self):
        for each in self:
            if each.order_id.type == 'amc':
                products = self.env['product.product'].search([('recurring_invoice', '=', True),('sale_ok','=',True)])
                each.product_ids = products.ids
            elif each.order_id.type == 'vas':
                # products = self.env['product.product'].search([('sale_ok','=',True),('service_tracking','!=', 'no')])
                products = self.env['product.product'].search([('sale_ok','=',True)])
                each.product_ids = products.ids
            else:
                each.product_ids = False






    

   

