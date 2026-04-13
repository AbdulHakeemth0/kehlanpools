from odoo import api, fields, models, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, format_date
from odoo.addons.sale_subscription.models.sale_order import SUBSCRIPTION_PROGRESS_STATE
from odoo.exceptions import UserError
import re


class SaleOrder(models.Model):
    _inherit = "sale.order"
    # _rec_names_search = ['name', 'm_number']
    
    
    m_number = fields.Char(string = "M-Number",tracking=True)
    external_project = fields.Boolean(string="External Project")
    job_number = fields.Char(string = "Job-Number")
    vas_job_number = fields.Many2one('project.project',string = "AMC Job-Number")
    amc_sequence = fields.Char('Sequence No.',copy=False, default=lambda self: _('New'))
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
    discount = fields.Float(string ='Discount.', store = True,related ='pricing_structure_discount',digits=(16,3))
    subtotal = fields.Float(string = 'Subtotal',compute="_compute_subtotal",  store = True,digits=(16,3))
    total_cost = fields.Float(compute="_compute_total_cost",store=True, digits=(16,3))
    company_over_head = fields.Float(string='Company Over Head %',store=True)
    over_head = fields.Float(string='Company Over Head',store=True,compute="_compute_company_overhead",digits=(16,3))
    profit_margin = fields.Float(compute="_compute_profit_margin",store=True,digits=(16,3)) 
    total_quote_amount = fields.Float(compute="_compute_total_quote_amount",store=True,digits=(16,3))
    amount_tax_pricing_structure = fields.Monetary(string ='Taxes ',related ='amount_tax')
    amount_total_with_tax = fields.Monetary(related ='amount_total', string="Total ")
    subject = fields.Char(string="Subject")
    team_lead_id = fields.Many2one('hr.employee',string="Team Lead")
    team_lead_ids = fields.Binary('hr.employee',compute="_compute_team_lead")
    technician_ids = fields.Many2many('hr.employee',compute="_compute_technician_id_domain")
    members_ids = fields.Many2many('hr.employee', string="Technicians")
    pricing_structure_discount = fields.Float(string="Discount",digits=(16,3))
    pool_specification_ids = fields.One2many(
        string='pool specification',
        comodel_name='pool.specification.line.sale',
        inverse_name='sale_pool_specification_id',
    )
    pool_dimension_ids = fields.One2many(
        string='pool dimension',
        comodel_name='pool.dimension.sale',
        inverse_name='sale_pool_dimension_id',
    )
    pricing_structure_ids = fields.One2many(
        string='pricing structure',
        comodel_name='pricing.structure.sale',
        inverse_name='sale_pricing_structure_id',
    )
    mep_equipment_ids = fields.One2many(
        string='mep equipment specifications',
        comodel_name='mep.equipment.specifications.sale',
        inverse_name='sale_mep_equipment_id',
    )
    sale_chemical_use_line_ids = fields.One2many(
        string='Chemicals in use',
        comodel_name='sale.chemical.use.line',
        inverse_name='sale_order_id',
    )
    sale_manpower_line_ids = fields.One2many(
        string='Manpower Provision',
        comodel_name='sale.manpower.line',
        inverse_name='sale_order_id',
    )
    approved_by = fields.Many2one("res.users", string="Approved By", copy=False)
    reject_reason = fields.Char(string = 'Rejected Reason')
    rejected_by = fields.Many2one('res.users',string = 'Rejected By')
    
    @api.depends('validity_date')
    def _compute_team_lead(self):
        for each in self:
            team_leads = self.env['hr.employee'].sudo().search([('is_team_lead','=',True)])
            if team_leads:
                team = []
                for team_lead in team_leads:
                    team.append(team_lead.id)
                if team:
                    each.team_lead_ids = team
                else:
                    each.team_lead_ids = []
            else:
                each.team_lead_ids = []

    @api.depends('team_lead_id')
    def _compute_technician_id_domain(self):
        for each in self:
            mems_ids = []
            if each.team_lead_id:
                team_id = self.env['hr.employee.team'].sudo().search([('team_lead_id', '=', each.team_lead_id.id)])
                if team_id:
                    for each_mem in team_id.members_ids:
                        mems_ids.append(each_mem.id)
                each.technician_ids = mems_ids
            else:
                mems_ids = []
                each.technician_ids = mems_ids
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'm_number' not in vals or vals['m_number'] == _('New'):
                vals['m_number'] = self.env['ir.sequence'].next_by_code('sale.mo.number') or _('New')
            if 'type' in vals:
                if 'is_revision' in vals and vals.get('is_revision') == False:
                    if vals['type'] == _('amc' ):
                        amc = self.env['ir.sequence'].next_by_code('sale.amc.sequence') or _('New')
                        if vals['m_number']:
                            vals['amc_sequence'] = amc + '/' + 'AMC#' + vals['m_number']
                        else:
                            vals['amc_sequence'] = amc + '/' + 'AMC'
                        test_seq = self.env['ir.sequence'].next_by_code('sale.amc.custom') or _('New')
                        vals['name'] = test_seq
                        if vals.get('external_project') == True:
                            project_seq = vals.get('job_number')
                            vals['name'] = test_seq + '/' + project_seq
                        if vals.get('vas_job_number'):
                            project_id_seq = self.env['project.project'].browse(vals.get('vas_job_number')).sequence_no if self.env['project.project'].browse(vals.get('vas_job_number')).sequence_no else False
                            if project_id_seq:
                                vals['name'] = test_seq + '/' + project_id_seq
                        # if 'is_revision' in vals and vals.get('is_revision') == True:
                        #     test_seq = self.env['ir.sequence'].next_by_code('sale.amc.custom') or _('New')
                        #     number = vals.get('revision_number')+1
                        #     if vals.get('external_project') == True:
                        #         project_seq = vals.get('job_number')
                        #         vals['name'] = test_seq + '/' + project_seq + f"/RE/0{number}"
                        #     if vals.get('vas_job_number'):
                        #         project_id_seq = self.env['project.project'].browse(vals.get('vas_job_number')).sequence_no if self.env['project.project'].browse(vals.get('vas_job_number')).sequence_no else False
                        #         if project_id_seq:
                        #             vals['name'] = test_seq + '/' + project_id_seq + f"/RE/0{number}"
                    if vals['type'] == _('vas'):
                        test = self.env['ir.sequence'].next_by_code('sale.vas.custom') or _('New')
                        if  vals['m_number']:
                            test_name = test + '/' + vals['m_number']
                            vals['name'] = test_name 
                        else:
                            test_name = test + '/' + 'NP'
                            vals['name'] = test_name
                # if 'is_revision' in vals:
                #     if vals.get('type') == _('vas') and vals.get('is_revision') == True:
                #         test = self.env['ir.sequence'].next_by_code('sale.vas.custom') or _('New')
                #         number = vals.get('revision_number')+1
                #         if  vals['m_number']:
                #             test_name = test + '/' + vals['m_number'] + f"/RE/0{number}"
                #             vals['name'] = test_name 
                #         else:
                #             test_name = test + '/' + 'NP' + f"/RE/0{number}"
                #             vals['name'] = test_name
                         
        return super().create(vals_list)

    def action_quotation_sent(self):
        """ Mark the given draft quotation(s) as sent.

        :raise: UserError if any given SO is not in draft state.
        """
        if any(order.state not in ('draft','approved') for order in self):
            raise UserError(_("Only draft orders can be marked as sent directly."))

        for order in self:
            order.message_subscribe(partner_ids=order.partner_id.ids)
            
        self.write({'state': 'sent'})

    # def write(self, vals):
    #     res = super(SaleOrder,self).write(vals)
    #     if vals.get('vas_job_number'):
    #         project_id_seq = self.env['project.project'].browse(vals.get('vas_job_number')).sequence_no if self.env['project.project'].browse(vals.get('vas_job_number')).sequence_no else False
    #         seq = self.name + f"/{project_id_seq}"
    #         self.name = seq
    #     return res
    
    def _prepare_upsell_renew_order_values(self, subscription_state):
        values = super(SaleOrder, self)._prepare_upsell_renew_order_values(subscription_state)
        values['type']=self.type
        return values
    
    @api.onchange('m_number')
    def onchange_m_number(self):
        if self.m_number:
            customer_id = self.env['res.partner'].search([('customer_rank', '!=', 0),('code', '=', self.m_number)])
            for each in customer_id:
                if each:
                    self.partner_id = each.id

    @api.onchange('no_of_pools')
    def _onchange_pool_dimension(self):
        # if not self.opportunity_id:
        if self.no_of_pools and self.no_of_pools > 0:
            self.pool_dimension_ids = [(5, 0, 0)]
            dimension_lines = []
            for pool in range(self.no_of_pools):

                dimension_lines.append((0, 0, {
                    'pool_dimension_sl_no': pool + 1,
                }))

            self.pool_dimension_ids = dimension_lines
            
            
    @api.onchange('pool_type')
    def _onchange_pool_type(self):
        if self.type == 'amc':
            if self.pool_type =='swimming_pool':
                self.subject ='ANNUAL MAINTENANCE OF SKIMMER SWIMMING POOL'
            if self.pool_type =='water_feature':
                self.subject ='ANNUAL MAINTENANCE OF WATER FEATURE'
            if self.pool_type =='other':    
                self.subject =''


    def write(self, vals):
        res = super(SaleOrder,self).write(vals)
        for each in self:
            if each.total_quote_amount:  
                product_tmpl_id = self.env['product.template'].search([('is_amc_product','=', True)],limit=1)    
                if product_tmpl_id:
                    product_id = self.env['product.product'].search([('product_tmpl_id','=', product_tmpl_id.id)])
                    line_id = each.order_line.filtered(lambda l:l.product_id.id == product_id.id)
                    if len(line_id) > 1:
                        line_id = line_id[0]     
                    if each.type == 'amc' and line_id:
                        if 'order_line' in vals:
                            line_id.write({
                                    'product_template_id':product_tmpl_id.id,
                                    'product_id':product_id.id,
                                    'product_uom_qty':line_id.product_uom_qty,
                                    'service_property_location': product_id.description_sale if product_id.description_sale else 'Provisioning of skilled technician for cleaning and maintenance of skimmer swimming pool',
                                    'product_uom':each.plan_id.uom_id.id if  each.plan_id.uom_id else  product_tmpl_id.uom_id.id,
                                    'price_unit':each.total_quote_amount,
                                    'order_id':each.id,
                                    'name':product_tmpl_id.name
                                })
                            if isinstance(vals['order_line'][0], (list, tuple)) and len(vals['order_line'][0]) >= 3:
                                if vals['order_line'][0][0] in (0, 1) and isinstance(vals['order_line'][0][2], dict):
                                    if 'service_property_location' in vals['order_line'][0][2]:
                                        line_id.write({
                                            'service_property_location': vals['order_line'][0][2]['service_property_location']
                                        })
                        if 'pricing_structure_ids' in vals or 'pricing_structure_ids' in self:
                            if line_id:
                                line_id.write({
                                    'price_unit':each.total_quote_amount
                                })
                            else:
                                line_id.create({
                                    'product_template_id':product_tmpl_id.id,
                                    'product_id':product_id.id,
                                    'product_uom_qty':1,
                                    'service_property_location': product_id.description_sale if product_id.description_sale else 'Provisioning of skilled technician for cleaning and maintenance of skimmer swimming pool',
                                    'product_uom':each.plan_id.uom_id.id if  each.plan_id.uom_id else  product_tmpl_id.uom_id.id,
                                    'price_unit':each.total_quote_amount,
                                    'order_id':each.id,
                                    'name':product_tmpl_id.name
                                })
                    if each.pricing_structure_ids and not line_id:
                        line_id.create({
                                'product_template_id':product_tmpl_id.id,
                                'product_id':product_id.id,
                                'product_uom_qty':1,
                                'service_property_location': product_id.description_sale if product_id.description_sale else 'Provisioning of skilled technician for cleaning and maintenance of skimmer swimming pool',
                                'product_uom':each.plan_id.uom_id.id if  each.plan_id.uom_id else  product_tmpl_id.uom_id.id,
                                'price_unit':each.total_quote_amount,
                                'order_id':each.id,
                                'name':product_tmpl_id.name
                            })
        if vals.get('vas_job_number'):
            if not self.original_sale_order_id:
                project_id_seq = self.env['project.project'].browse(vals.get('vas_job_number')).sequence_no if self.env['project.project'].browse(vals.get('vas_job_number')).sequence_no else False
                seq = self.name[:18] + f"/{project_id_seq}"
                self.name = seq
        if vals.get('job_number'):
            if not self.original_sale_order_id:
                seq = self.name[:18] 
                job_no = vals.get('job_number')
                self.name = seq + f"/{job_no}"
        return res

    @api.onchange('no_of_pools')
    def _onchange_no_of_pools(self):
        if self.no_of_pools and self.no_of_pools > 0:
            self.pool_specification_ids = [(5, 0, 0)]

            self.pricing_structure_ids = [(5, 0, 0)]
            self.sale_chemical_use_line_ids = [(5, 0, 0)]
            self.sale_manpower_line_ids = [(5, 0, 0)]

            pricing_structure_lines = []
            specification_lines = []
            sale_chemical_use_lines = []
            sale_manpower_lines = []

            manpower = {'1.1 Technician':2,'1.2 PPM Team Share':2,'1.3 Supervisory Share':5,'1.4 Mechanical Engineer Share':0,'1.5 Specialist Share':0}
            cons_dict = {'2.1 Calcium hypochlorite':1,'2.2 Calcium hypochlorite - HTH':2.500,'2.3 Sodium bisulfate':0.5,'2.4 Sodium bimetasulfate':1,'2.5 Cyranuric acid':1.8,'2.6 Chlorine tablet':1,'2.7 Algacid':1.8,'2.8 Puresan':0,'2.9 Salt':0}
          
            cons_dict1 = {'Calcium hypochlorite':2,'Sodium bisulfate':0.5,'Sodium bimetasulfate':1,'Cyranuric acid':1.8,'Chlorine tablet':2,'Algacid':1.8,'Puresan':0,'Salt':0}
            manpower1 = {'Technician':2,'PPM Team Share':2,'Supervisory Share':5,'Mechanical Engineer Share':0,'Specialist Share':0}

            tool_dict = {'3.1 Cleaning kit':2.5,'3.2 Tool box':0,'3.3 Miscl':1}
            others_dict = {'4.1 Transportation':5,'4.2 Food':0}

            manpower_list = ['1.1 Technician','1.2 PPM Team Share','1.3 Supervisory Share','1.4 Mechanical Engineer Share','1.5 Specialist Share']
            cons_list = ['2.1 Calcium hypochlorite','2.2 Sodium bisulfate','2.3 Sodium bimetasulfate','2.4 Cyranuric acid','2.5 Chlorine tablet','2.6 Algacid','2.7 Puresan','2.8 Sodium bicarbonate']
            tool_list = ['3.1 Cleaning kit','3.2 Tool box','3.3 Miscl']
            others_list = ['4.1 Transportation','4.2 Food']

            for pool in range(self.no_of_pools):

                # specification_lines.append((0, 0, {
                #     'pool_specification_sl_no': pool + 1,
                    
                    
                # }))
                if self.no_of_pools >= 1:
                    specification_lines.append((0, 0, {
                        'pool_specification_sl_no': pool + 1,
                        'pool_loc':'backyard',
                        'asset_location':'outdoor',
                        'filteration_system':'skimmer',
                        'auto_dozing_system':'na',
                        'disinfection_system':'na',
                        'pool_finishing_type':'tiles',
                        'distance_from_camp':40,
                        'distance_from_other_pools':40,
                        'pools_in_circuit':1,
                        'visit_frequency':2,
                        'visit_type':'weekly'

                        
                    }))  

                pricing_structure_lines.append((0, 0, {
                    'display_type': 'line_section',
                    'name': f'POOL {pool + 1}',
                }))
                sale_chemical_use_lines.append((0, 0, {
                    'display_type': 'line_section',
                    'name': f'POOL {pool + 1}',
                }))
                sale_manpower_lines.append((0, 0, {
                    'display_type': 'line_section',
                    'name': f'POOL {pool + 1}',
                }))

                pricing_structure_lines.append((0, 0, {
                    'display_type': 'line_section',
                    'name': '1.Manpower',
                }))

                for k,v in manpower.items():
                    boq =0.0
                    if k [:3] =='1.1':
                        boq =8.0
                    elif k [:3] =='1.3':
                        boq =1.0
                    else:
                       boq =0.0 
                    pricing_structure_lines.append((0, 0, {
                        'name': k,
                        'pool_structure_sl_no': pool + 1,
                        'is_manpower':True,
                        'description': '',
                        'unit': False,  
                        'boq': boq,
                        'unit_rate': v,
                        'amount': 0.0,
                        'remarks': '',
                    }))
                
                for man, man1 in manpower1.items():
                    sale_manpower_lines.append((0, 0, {
                        'name': man,
                        'pool_structure_sl_no': pool + 1,
                    }))

                # for line in range(0, len(manpower_list)):
                #     pricing_structure_lines.append((0, 0, {
                #         'name': manpower_list[line],
                #         'pool_structure_sl_no': pool + 1,
                #         'is_manpower':True,
                #         'description': '',
                #         'unit': False,  
                #         'boq': 0.0,
                #         'unit_rate': 0.0,
                #         'amount': 0.0,
                #         'remarks': '',
                #     }))
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
                boq_mapping = {
                    '2.1': 4.0,
                    '2.2': 0.0,
                    '2.3': 6.0,
                    '2.4': 0.5,
                    '2.5': 0.5,
                    '2.6': 0.5,
                    '2.7': 0.5,
                    '2.8': 0.0,
                    '2.9': 0.0
                }

                for k, v in cons_dict.items():
                    boq = 0.0  
                    for prefix in boq_mapping:
                        if k[:3] == prefix:
                            boq = boq_mapping[prefix]
                            break

                    pricing_structure_lines.append((0, 0, {
                        'name': k,
                        'pool_structure_sl_no': pool + 1,
                        'is_consumables': True,
                        'description': '',
                        'unit': False,
                        'boq': boq,
                        'unit_rate': v,
                        'amount': 0.0,
                        'remarks': '',
                    }))
                
                for chem, chem1 in cons_dict1.items():
                    sale_chemical_use_lines.append((0, 0, {
                        'name': chem,
                        'pool_structure_sl_no': pool + 1,
                    }))

                # for line in range(0, len(cons_list)):
                #     pricing_structure_lines.append((0, 0, {
                #         'name': cons_list[line],
                #         'pool_structure_sl_no': pool + 1,
                #         'is_consumables':True,
                #         'description': '',
                #         'unit': False,
                #         'boq': 0.0,
                #         'unit_rate': 0.0,
                #         'amount': 0.0,
                #         'remarks': '',
                #     }))
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
                for k,v in tool_dict.items():
                    boq =0.0
                    if k [:3] =='3.1' or k[:3] =='3.3':
                        boq =1.0
                    else:
                       boq =0.0 
                    pricing_structure_lines.append((0, 0, {
                        'name': k,
                        'pool_structure_sl_no': pool + 1,
                        'is_toolsequipment':True,
                        'description': '',
                        'unit': False,
                        'boq': boq,
                        'unit_rate': v,
                        'amount': 0.0,
                        'remarks': '',
                    }))
                # for line in range(0, len(tool_list)):
                #     pricing_structure_lines.append((0, 0, {
                #         'name': tool_list[line],
                #         'pool_structure_sl_no': pool + 1,
                #         'is_toolsequipment':True,
                #         'description': '',
                #         'unit': False,
                #         'boq': 0.0,
                #         'unit_rate': 0.0,
                #         'amount': 0.0,
                #         'remarks': '',
                #     }))
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
                for k,v in others_dict.items():
                    boq =0.0
                    if k [:3] =='4.1':
                        boq =1.0
                    else:
                       boq =0.0 
                    pricing_structure_lines.append((0, 0, {
                        'name': k,
                        'pool_structure_sl_no': pool + 1,
                        'is_otheritems':True,
                        'description': '',
                        'unit': False, 
                        'boq': boq,
                        'unit_rate': v,
                        'amount': 0.0,
                        'remarks': '',
                    }))
                # for line in range(0, len(others_list)): 
                #     pricing_structure_lines.append((0, 0, {
                #         'name': others_list[line],
                #         'pool_structure_sl_no': pool + 1,
                #         'is_otheritems':True,
                #         'description': '',
                #         'unit': False, 
                #         'boq': 0.0,
                #         'unit_rate': 0.0,
                #         'amount': 0.0,
                #         'remarks': '',
                #     }))
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
            self.sale_chemical_use_line_ids = sale_chemical_use_lines
            self.sale_manpower_line_ids = sale_manpower_lines


    # @api.onchange('no_of_pools','no_of_line_manpower','no_of_line_consumables','no_of_line_toolsandequipments','no_of_line_otheritems')
    # def _onchange_no_of_pools(self):
    #     if not self.opportunity_id:
    #         if self.no_of_pools and self.no_of_pools > 0:
    #             self.pool_dimension_ids = [(5, 0, 0)]
    #             self.pool_specification_ids = [(5, 0, 0)]
    #             self.pricing_structure_ids = [(5, 0, 0)]
                
    #             dimension_lines = []
    #             specification_lines = []
    #             pricing_structure_lines = []

    #             for pool in range(self.no_of_pools):

    #                 dimension_lines.append((0, 0, {
    #                     'pool_dimension_sl_no': pool + 1,
    #                 }))
    #                 specification_lines.append((0, 0, {
    #                     'pool_specification_sl_no': pool + 1,
    #                 }))

    #                 pricing_structure_lines.append((0, 0, {
    #                     'display_type': 'line_section',
    #                     'name': f'POOL {pool + 1}',
    #                 }))

    #                 pricing_structure_lines.append((0, 0, {
    #                     'display_type': 'line_section',
    #                     'name': 'Manpower',
    #                 }))
    #                 for line in range(1, self.no_of_line_manpower + 1):
    #                     pricing_structure_lines.append((0, 0, {
    #                         'name': f'Manpower Item {line}',
    #                         'pool_structure_sl_no': pool + 1,
    #                         'is_manpower':True,
    #                         'description': '',
    #                         'unit': False,  
    #                         'boq': 0.0,
    #                         'unit_rate': 0.0,
    #                         'amount': 0.0,
    #                         'total_amount': 0.0,
    #                         'remarks': '',
    #                     }))
    #                 pricing_structure_lines.append((0, 0, {
    #                     'name': f'Total',
    #                     'pool_structure_sl_no': pool + 1,
    #                     'is_manpower':True,
    #                     'is_sum_line':True,
    #                     'total_amount': 0.0,
    #                 }))

    #                 pricing_structure_lines.append((0, 0, {
    #                     'display_type': 'line_section',
    #                     'name': 'Consumables',  
    #                 }))
    #                 for line in range(1, self.no_of_line_consumables + 1):
    #                     pricing_structure_lines.append((0, 0, {
    #                         'name': f'Consumable Item {line}',
    #                         'pool_structure_sl_no': pool + 1,
    #                         'is_consumables':True,
    #                         'description': '',
    #                         'unit': False,
    #                         'boq': 0.0,
    #                         'unit_rate': 0.0,
    #                         'amount': 0.0,
    #                         'total_amount': 0.0,
    #                         'remarks': '',
    #                     }))
    #                 pricing_structure_lines.append((0, 0, {
    #                     'name': f'Total',
    #                     'pool_structure_sl_no': pool + 1,
    #                     'is_consumables':True,
    #                     'is_sum_line':True,
    #                     'total_amount': 0.0,
    #                 }))

    #                 pricing_structure_lines.append((0, 0, {
    #                     'display_type': 'line_section',
    #                     'name': 'Tools & Equipment',
    #                 }))
    #                 for line in range(1, self.no_of_line_toolsandequipments + 1):
    #                     pricing_structure_lines.append((0, 0, {
    #                         'name': f'Tools & Equipment Item {line}',
    #                         'pool_structure_sl_no': pool + 1,
    #                         'is_toolsequipment':True,
    #                         'description': '',
    #                         'unit': False,
    #                         'boq': 0.0,
    #                         'unit_rate': 0.0,
    #                         'amount': 0.0,
    #                         'total_amount': 0.0,
    #                         'remarks': '',
    #                     }))
    #                 pricing_structure_lines.append((0, 0, {
    #                     'name': f'Total',
    #                     'pool_structure_sl_no': pool + 1,
    #                     'is_toolsequipment':True,
    #                     'is_sum_line':True,
    #                     'total_amount': 0.0,
    #                 }))

    #                 pricing_structure_lines.append((0, 0, {
    #                     'display_type': 'line_section',
    #                     'name': 'Other Items',
    #                 }))
    #                 for line in range(1, self.no_of_line_otheritems + 1): 
    #                     pricing_structure_lines.append((0, 0, {
    #                         'name': f'Other Items Item {line}',
    #                         'pool_structure_sl_no': pool + 1,
    #                         'is_otheritems':True,
    #                         'description': '',
    #                         'unit': False, 
    #                         'boq': 0.0,
    #                         'unit_rate': 0.0,
    #                         'amount': 0.0,
    #                         'total_amount': 0.0,
    #                         'remarks': '',
    #                     }))
    #                 pricing_structure_lines.append((0, 0, {
    #                     'name': f'Total',
    #                     'pool_structure_sl_no': pool + 1,
    #                     'is_otheritems':True,
    #                     'is_sum_line':True,
    #                     'total_amount': 0.0,
    #                 }))

    #             self.pool_dimension_ids = dimension_lines
    #             self.pool_specification_ids = specification_lines
    #             self.pricing_structure_ids = pricing_structure_lines

    # @api.onchange('pricing_structure_ids')
    # def _onchange_total(self):
    #     total_amount = 0
    #     for record in self.pricing_structure_ids:
    #         if record.display_type == 'line_section':
    #             pass
    #         elif not record.display_type == 'line_section' and not record.is_sum_line:
    #             total_amount += record.amount
    #         elif record.is_sum_line:
    #             t_amount = (total_amount) * (self.profit_margin_percentage)
    #             p_amount = t_amount/100
    #             record.total_amount = total_amount + p_amount
    #             total_amount = 0


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
                record.amount = total_amount 
                # + p_amount  
                
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

    @api.depends('total_cost','over_head','profit_margin')             
    def _compute_subtotal(self):
        for rec in self:
            if rec.total_cost:
                rec.subtotal = rec.total_cost + rec.over_head +rec.profit_margin
            else:
                rec.subtotal = 0            

    @api.depends('company_over_head','total_cost')
    def _compute_company_overhead(self):
        for order in self:
            if order.total_cost:
                over_head = (order.total_cost) * (order.company_over_head)
                order.over_head = over_head/100
            else:
                order.over_head = 0

    @api.depends('total_cost','profit_margin_percentage')
    def _compute_profit_margin(self):
        for lead in self:
            if lead.total_cost:
                t_amount = (lead.total_cost) * (lead.profit_margin_percentage)
                lead.profit_margin = t_amount/100
            else:
                lead.profit_margin = 0
    # to pass the total quote amount in Unit price of sale order line (AMC)
    # @api.onchange('total_quote_amount')
    # def _onchange_total_quote_amount(self):
    #     if self.type == 'amc':
    #         product_tmpl_id = self.env['product.template'].search([('is_amc_product','=', True)])
    #         self.order_line.create({
    #             'product_template_id':product_tmpl_id.id,
    #             'product_uom_qty':1,
    #             'product_uom':product_tmpl_id.uom_id.id,
    #             'price_unit':self.total_quote_amount,
    #             'order_id':self.id
    #         })
            # for line in self.order_line:
            #     if self.total_quote_amount:
            #         line.price_unit = self.total_quote_amount

    @api.depends('total_cost', 'company_over_head', 'profit_margin','pricing_structure_discount')
    def _compute_total_quote_amount(self):
        for lead in self:
            company_overhead = (lead.total_cost * lead.company_over_head / 100) if lead.total_cost else 0
            lead.total_quote_amount = (lead.total_cost + company_overhead + lead.profit_margin) - lead.pricing_structure_discount
            
    # def action_rearrange_sequence(self):
    #     amc_quotations = self.env['sale.order'].sudo().search([('type', '=', 'amc'),('is_revision','!=',True)],order='id asc')
    #     amc_number = 1000001
    #     for amc in amc_quotations:
    #         if amc.name:
    #             match = re.match(r'([^\d]+)(\d+)(/.+)?', amc.name)
    #             if match:
    #                 prefix, number, suffix = match.groups()
    #                 suffix = suffix or ''
    #             new_number = f"{amc_number:08d}"
    #             new_name = f"{prefix}{new_number}{suffix}"
    #             amc.name = new_name
    #             amc_number += 1
    #         child_ids = self.env['sale.order'].search([('original_sale_order_id','=',amc.id)],order='id asc')
    #         r_num = 1
    #         for child in child_ids:
    #             child_name = f"{amc.name}/R{r_num:02d}"
    #             child.name = child_name
    #             r_num += 1
                    
    def update_next_invoice_date(self):
        for rec in self.filtered(lambda l:l.contract_start_date):
            rec.start_date = rec.contract_start_date
            if rec.plan_id.is_weekly:
                rec.next_invoice_date = rec.contract_start_date + timedelta(days=7)
            if rec.plan_id.is_monthly:
                rec.next_invoice_date = rec.contract_start_date + relativedelta(months=1)
            if rec.plan_id.is_quaterly:
                rec.next_invoice_date = rec.contract_start_date + relativedelta(months=3)
            if rec.plan_id.is_bi_yearly:
                rec.next_invoice_date = rec.contract_start_date + relativedelta(months=6)
            if rec.plan_id.is_yearly:
                rec.next_invoice_date = rec.contract_start_date + relativedelta(months=12)
        
    
    def update_sale_invoice_description(self):
        for rec in self.filtered(lambda l:l.contract_start_date and l.next_invoice_date):
            lang_code = rec.partner_id.lang
            for line in rec.order_line.invoice_lines:
                duration = rec.plan_id.billing_period_display

                new_period_start, new_period_stop, ratio, number_of_days = line.sale_line_ids._get_invoice_line_parameters()
                if rec.contract_start_date:
                    new_period_start = rec.contract_start_date
                if rec.next_invoice_date:
                    new_period_stop = rec.next_invoice_date - timedelta(days=1)

                description = line.sale_line_ids.product_id.name
                if line.sale_line_ids.recurring_invoice:
                    format_start = format_date(self.env, new_period_start, lang_code=lang_code)
                    format_next = format_date(self.env, new_period_stop, lang_code=lang_code)
                    start_to_next = _("%(start)s to %(next)s", start=format_start, next=format_next)
                    description += f"\n{duration} {start_to_next}"
                    line.name = description
                    line.product_label = description
                    
    def button_reject_request(self):
        self.is_revise = True 
        return {
            "name": _("Reject"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "reject.reason.wizard",
            "view_id": self.env.ref("bi_sale.sale_sub_reject_wizard_view").id,
            "target": "new",
            "context": {"default_sale_order_id": self.id},
        }           

    def button_approved(self):     
        for rec in self:
            rec.state = "approved"
            rec.approved_by = self.env.user.id
                    
    

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _valid_field_parameter(self, field, name):
        if name == 'tracking':
            return True
        return super(SaleOrderLine, self)._valid_field_parameter(field, name)
    
    struct_name = fields.Char(string='Name', tracking=True,store=True)
    image = fields.Binary(string="Images")
    
    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)
        lang_code = self.order_id.partner_id.lang

        duration = self.order_id.plan_id.billing_period_display
        if self.order_id.is_subscription:
            new_period_start, new_period_stop, ratio, number_of_days = self._get_invoice_line_parameters()
            if self.order_id.contract_start_date:
                new_period_start = self.order_id.contract_start_date
            if self.order_id.next_invoice_date:
                new_period_stop = self.order_id.next_invoice_date - timedelta(days=1)

            description = self.product_id.name
            if self.recurring_invoice and self.order_id.type == 'amc':
                format_start = format_date(self.env, new_period_start, lang_code=lang_code)
                format_next = format_date(self.env, new_period_stop, lang_code=lang_code)
                start_to_next = _("%(start)s to %(next)s", start=format_start, next=format_next)
                description += f"\n {start_to_next}"
                res['name'] = description
                res['product_label'] = description

        return res
    
    # @api.onchange('product_id')
    # def _onchange_service_property_location(self):
    #     for rec in self:
    #         rec.service_property_location = "Provisioning of skilled technician for cleaning and maintenance of skimmer swimming pool"

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        posted_moves = super()._post(soft=soft)
        automatic_invoice = self.env.context.get('recurring_automatic')
        all_subscription_ids = set()
        for move in posted_moves:
            if not move.invoice_line_ids.subscription_id:
                continue
            if move.move_type != 'out_invoice':
                if move.move_type == 'out_refund':
                    body = _("The following refund %s has been made on this contract. Please check the next invoice date if necessary.", move._get_html_link())
                    for so in move.invoice_line_ids.subscription_id:
                        # Normally, only one subscription_id per move, but we handle multiple contracts as a precaution
                        so.message_post(body=body)
                continue

            for aml in move.invoice_line_ids:
                if not aml.subscription_id or aml.is_downpayment:
                    continue
                all_subscription_ids.add(aml.subscription_id.id)
        all_subscriptions = self.env['sale.order'].browse(all_subscription_ids)
        for subscription in all_subscriptions:
            # Invoice validation will increment the next invoice date
            if subscription.subscription_state in SUBSCRIPTION_PROGRESS_STATE + ['6_churn']:
                # We increment the next invoice date for progress sub and churn one.
                # Churn sub are reopened in the _post_process of payment transaction.
                # Renewed sub should not be incremented as the renewal is the running contract.
                # Invoices for renewed contract can be posted when the delivered products arrived after the renewal date.

                # last_invoice_end_date = subscription.order_line.invoice_lines._get_max_invoiced_date()

                if subscription.plan_id.is_weekly:
                    last_invoice_end_date = self.invoice_date + timedelta(days=7)
                if subscription.plan_id.is_monthly:
                    last_invoice_end_date = self.invoice_date + relativedelta(months=1)
                if subscription.plan_id.is_quaterly:
                    last_invoice_end_date = self.invoice_date + relativedelta(months=3)
                if subscription.plan_id.is_bi_yearly:
                    last_invoice_end_date = self.invoice_date + relativedelta(months=6)
                if subscription.plan_id.is_yearly:
                    last_invoice_end_date = self.invoice_date + relativedelta(months=12)

                # last_invoice_end_date = last_invoice_end_date - timedelta(days=1)
                subscription.next_invoice_date = last_invoice_end_date if last_invoice_end_date else subscription.start_date
                if all(subscription.order_line.mapped(lambda line: line._is_postpaid_line())):
                    subscription.next_invoice_date += subscription.plan_id.billing_period
                subscription.last_reminder_date = False
            subscription.pending_transaction = False
        if all_subscriptions:
            # update the renewal quotes to start at the next invoice date values
            renewal_quotes = self.env['sale.order'].search([
                ('subscription_id', 'in', all_subscriptions.ids),
                ('subscription_state', '=', '2_renewal'),
                ('state', 'in', ['draft', 'sent'])])
            for quote in renewal_quotes:
                next_invoice_date = quote.subscription_id.next_invoice_date
                if not quote.start_date or quote.start_date < next_invoice_date:
                    quote.update({
                        'next_invoice_date': next_invoice_date,
                        'start_date': next_invoice_date,
                    })
        if not automatic_invoice:
            all_subscriptions._post_invoice_hook()

        return posted_moves
    
    