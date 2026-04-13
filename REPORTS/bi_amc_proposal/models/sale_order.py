from odoo import  _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_amc = fields.Boolean(
        string="Is AMC",
        compute='_compute_is_amc',
        store=True
    )
    type_shape = fields.Char(string="Type / Shape")
    size = fields.Char(string="Size")
    depth = fields.Char(string="Depth")
    surface_area = fields.Char(string="Surface Area")
    volume = fields.Char(string="Volume")
    completion_line_ids = fields.One2many('completion.period.line', 'sale_order_id',
                                           string="Completion Period ")
    
    
    @api.depends('type')
    def _compute_is_amc(self):
        for record in self:
            record.is_amc = (record.type == 'amc')
            if record.is_amc:
                record.terms_condtion_corporate_ids = [(5, 0, 0)]  # Removes all existing lines
                record.specific_conditions_corporate_ids = [(5, 0, 0)]  # Removes all existing lines
                record.general_scope_corporate_ids = [(5, 0, 0)]  # Removes all existing lines
                record.detailed_scope_corporate_ids = [(5, 0, 0)]  # Removes all existing lines
                record.amc_scope_corporate_ids = [(5, 0, 0)]
                terms_condition_master = self.env['amc.corporate.terms.conditions'].search([])
                specific_conditions_master = self.env['amc.corporate.specific.conditions'].search([])
                general_scope_master = self.env['amc.corporate.general.scope.work'].search([])
                detailed_scope_master = self.env['amc.corporate.detail.scope.work'].search([])
                amc_scope_master = self.env['amc.corporate.scope.work'].search([])
                terms_conditions = [(0, 0, {'description': line.name}) for line in terms_condition_master]
                specific_conditions = [(0, 0, {'description': line.name}) for line in specific_conditions_master]
                general_scope = [(0, 0, {'description': line.name}) for line in general_scope_master]
                detailed_scope = [(0, 0, {'description': line.name}) for line in detailed_scope_master]
                amc_scope = [(0, 0, {'description': line.name}) for line in amc_scope_master]

                record.update({
                    'terms_condtion_corporate_ids': terms_conditions,
                    'specific_conditions_corporate_ids': specific_conditions,
                    'general_scope_corporate_ids': general_scope,
                    'detailed_scope_corporate_ids': detailed_scope,
                    'amc_scope_corporate_ids': amc_scope,
                })



    is_vas_template = fields.Boolean(string="Is VAS Template")
    is_vas_template1 = fields.Boolean(string="Is VAS Template 1")
    is_amc_non_corporate = fields.Boolean(string="Is AMC Non-Corporate")
    is_amc_corporate = fields.Boolean(string="Is AMC Corporate")

    report_template_id = fields.Many2one(
        'ir.actions.report',
        string="VAS Template",
        domain="[('is_vas_report', '=', True)]",
        help="Select the report template to use when printing this sale order."
    )
    report_template_amc_id = fields.Many2one(
        'ir.actions.report',
        string="AMC Template",
        domain="[('is_swimming_template', '=', True)]",
        help="Select the report template to use when printing this sale order."
    )
    report_template_amc_id_water = fields.Many2one(
        'ir.actions.report',
        string="AMC Template ",
        domain="[('is_water_template', '=', True)]",
        help="Select the report template to use when printing this sale order."
    )
    delivery_period = fields.Char(string="Delivery Period", help="Specify the delivery period for the order")
    filled_with = fields.Float(string="Filled With", help="Specify the filled amount in the order")
    offer_validity = fields.Char(string="Offer Validity")
    first_payment_percentage = fields.Float()
    second_payment_percentage = fields.Float()

    # Computed field to concatenate the percentages as a string
    terms_conditions_ids = fields.One2many('sale.order.terms.conditions', 'sale_order_id',
                                           string="Terms and Conditions")
    terms_condtion_corporate_ids = fields.One2many('sale.order.terms.conditions.corporate', 'sale_order_id',
                                           string="Terms and Conditions ")
    specific_conditions_ids = fields.One2many('sale.order.specific.conditions', 'sale_order_id',
                                              string="Specific Conditions")
    specific_conditions_corporate_ids = fields.One2many('sale.order.specific.conditions.corporate', 'sale_order_id',
                                              string="Specific Conditions ")
    general_scope_ids = fields.One2many('sale.order.general.scope', 'sale_order_id', string="General Scope of Work")
    general_scope_corporate_ids = fields.One2many('sale.order.general.scope.corporate', 'sale_order_id', string="General Scope of Work ")
    detailed_scope_ids = fields.One2many('sale.order.detailed.scope', 'sale_order_id', string="Detailed Scope of Work")
    detailed_scope_corporate_ids = fields.One2many('sale.order.detailed.scope.corporate', 'sale_order_id', string="Detailed Scope of Work ")
    amc_scope_ids = fields.One2many('sale.order.amc.scope', 'sale_order_id', string="AMC Scope of Work")
    amc_scope_corporate_ids = fields.One2many('sale.order.amc.scope.corporate', 'sale_order_id', string="AMC Scope of Work ")

    vas_exclusions= fields.One2many('vas.exclusion.line', 'order_id', string="Exclusions ")
    vas_warranty_details = fields.One2many('vas.warranty.line', 'order_id', string="Warranty Details ")
    warranty_exclusions_ids = fields.One2many('warranty.exclution.line', 'order_id', string="Exclusions Exclution")
    delivery_period_ids = fields.One2many('delivery.period.line', 'order_id', string="Delivery Period ")
    # detailed_specification_ids = fields.One2many('detailed.specification', 'sale_id', string="Detailed Specification")
    # client_exclusions_ids = fields.One2many('client.exclusion', 'sale_id', string="Exclusions",compute='_compute_related_fields', store=True, readonly=False)
    # warranty_details_ids = fields.One2many('warranty.details', 'sale_id', string="Warranty Details",compute='_compute_related_fields', store=True, readonly=False)
    amc_asset_details = fields.One2many(
        comodel_name='asset.line',
        inverse_name='sale_order_id',
        string='AMC Asset Details',
        readonly=False
    )
    payment_term_ids = fields.One2many('payment.line','sale_order_id',string='Payment Term ',readonly=False)

        

    @api.onchange('report_template_id')
    def _onchange_report_template_id(self):
        for order in self:
            report_name = order.report_template_id.report_name if order.report_template_id else ''
            order.is_vas_template = report_name == 'bi_amc_proposal.report_vas_proposal'
            order.is_vas_template1 = report_name == 'bi_amc_proposal.report_vas_proposal1'
            if order.report_template_id:
                order.write({
                        'client_exclusions_ids': [(5, 0, 0)],
                        'vas_exclusions': [(5, 0, 0)],
                        'vas_warranty_details': [(5, 0, 0)],
                        'warranty_details_ids': [(5, 0, 0)],
                        'warranty_exclusions_ids':[(5, 0, 0)],
                        'delivery_period_ids':[(5, 0, 0)],
                        'detailed_specification_ids': [(5, 0, 0)],
                        'completion_line_ids':[(5, 0, 0)],

                        'payment_term_vas_ids': [(5, 0, 0)],
                        'vas_warranty_ids': [(5, 0, 0)],

                        'payment_term_ids':[(5, 0, 0)],
                        'scope_of_work_ids': [(5, 0, 0)],

                    })
                # vas template 2
                if order.report_template_id.report_name == 'bi_amc_proposal.report_vas_proposal1':
                    master_client_exclusions = self.env['client.exclusion'].search([])
                    master_warranty_details = self.env['warranty.details'].search([])
                    master_specification_details = self.env['detailed.specification.master'].search([])

                    master_vas_warranty_exclusion = self.env['vas.warranty.exclusion'].search([])
                    vas_warranty_list = []
                    for vas_warranty in master_vas_warranty_exclusion:
                        vas_warranty_list.append((0, 0, {
                            'name': vas_warranty.description,
                        }))


                    # Vas payemt terms
                    
                    master_payment_terms = self.env['vas.payment.terms'].search([])
                    vas_payment_term = []
                    for payment_term in master_payment_terms:
                        vas_payment_term.append((0, 0, {
                            'description':payment_term.description,
                        }))
                                   

                    master_scope_of_work = self.env['scope.of.work'].search([])
                    vas_scope_of_work = []
                    for scope_for_work in master_scope_of_work:
                        vas_scope_of_work.append((0, 0, {
                            'description': scope_for_work.description,
                        }))

                    # vas_warranty_value = master_vas_warranty_exclusion.description

                    master_completion_period = self.env['completion.period.master'].search([])

                    warranty_list = []
                    for warranty in master_warranty_details:
                        if warranty.warranty_lines:
                            # warranty_list = []
                            for line in warranty.warranty_lines:
                                if line.display_type == 'line_section':
                                    warranty_list.append((0, 0, {
                                        'display_type': 'line_section',
                                        'name': line.name,
                                    }))
                                else:
                                    warranty_list.append((0, 0, {
                                        'name': line.name,
                                    }))       

                    client_exclusion_lines = [(0, 0, {"exclusion_id": excl.id}) for excl in master_client_exclusions]
                    warranty_detail_lines = [(0, 0, {"warranty_id": warranty.id}) for warranty in master_warranty_details]
                    completion_lines = [(0, 0, {"description": comp.description}) for comp in master_completion_period]
                    specification_lines = []
                    first_note_found = False
                    first_section_found = False
                    for spec_master in master_specification_details:
                        for spec_line in spec_master.specification_line_ids:
                            if spec_line.display_type == 'line_note' and not first_note_found:
                                heading_data = {
                                    "name": spec_line.name,  # This will be the heading
                                    "display_type": spec_line.display_type,
                                    "item": None,  # No item associated with note
                                    "qty": None,  # No quantity for note
                                    "uom_id": None,  # No UOM for note
                                    "tax_id": None,  # No tax for note
                                    "amount": None  # No amount for note
                                }
                                specification_lines.append((0, 0, heading_data))

                            elif spec_line.display_type == 'line_section' and not first_section_found:
                                section_data = {
                                    "name": spec_line.name,  # This will be the first section name
                                    "display_type": spec_line.display_type,
                                    "item": None,  # No item associated with section
                                    "qty": None,  # No quantity for section
                                    "uom_id": None,  # No UOM for section
                                    "tax_id": None,  # No tax for section
                                    "amount": None  # No amount for section
                                }
                                specification_lines.append((0, 0, section_data))
                            else:
                                line_data = {
                                    "item": spec_line.name,  # Item name
                                    "qty": spec_line.qty,  # Quantity
                                    "uom_id": spec_line.uom_id.id if spec_line.uom_id else False,  # Unit of Measure
                                    "tax_id": [(6, 0, spec_line.tax_id.ids)] if spec_line.tax_id else False,  # Tax
                                    "amount": spec_line.amount  # Amount
                                }
                                specification_lines.append((0, 0, line_data))
                    order.write({
                        'client_exclusions_ids': client_exclusion_lines,
                        'warranty_details_ids': warranty_list,
                        'detailed_specification_ids': specification_lines,
                        'scope_of_work_ids':vas_scope_of_work,

                        'vas_warranty_ids':vas_warranty_list,
                        'payment_term_vas_ids':vas_payment_term,

                        'completion_line_ids':completion_lines
                    })
                # vas tempalte 1
                elif order.report_template_id and order.report_template_id.report_name == 'bi_amc_proposal.report_vas_proposal':
                    master_vas_client_exclusions = self.env['product.exclusion'].search([])
                    master_vas_warranty_details = self.env['vas.warranty'].search([])
                    master_warranty_exclution = self.env['warranty.exclusion'].search([])
                    master_delivery_period = self.env['delivery.period'].search([])
                    vas_exclusion_lines = [(0, 0, {"description": excl.description}) for excl in
                                           master_vas_client_exclusions]
                    warranty_vas_lines = [(0, 0, {"description": warranty.description}) for warranty in
                                          master_vas_warranty_details]
                    warranty_exclution_lines = [(0, 0, {"description": war_exclu.description}) for war_exclu in
                                          master_warranty_exclution]
                    delivery_period_lines = [(0, 0, {"description": period.description}) for period in
                                          master_delivery_period]

                    master_client_exclusions = self.env['client.exclusion'].search([])
                    master_warranty_details = self.env['warranty.details'].search([])

                    client_exclusion_lines = [(0, 0, {"exclusion_id": excl.id}) for excl in master_client_exclusions]
                    warranty_detail_lines = [(0, 0, {"warranty_id": warranty.id}) for warranty in master_warranty_details]

                    payment_ids = self.env['payment.term.details'].search([])
                    value_list = [(0, 0, {'payment_term_id': each.id}) for each in payment_ids]

                    order.write({
                        'client_exclusions_ids': client_exclusion_lines,
                        'warranty_details_ids': warranty_detail_lines,
                        'vas_exclusions': vas_exclusion_lines,
                        'vas_warranty_details': warranty_vas_lines,
                        'warranty_exclusions_ids': warranty_exclution_lines,
                        'delivery_period_ids': delivery_period_lines,
                        'payment_term_ids': value_list,
                        # 'detailed_specification_ids': specification_lines
                    })
                else:
                    order.write({
                        'client_exclusions_ids': [(5, 0, 0)],
                        'warranty_details_ids': [(5, 0, 0)],
                        'detailed_specification_ids': [(5, 0, 0)],
                    })


            # if order.report_template_id:
                    # payment_ids = self.env['payment.term.details'].search([])
                    # value_list = []
                    # if payment_ids:
                    #     for each in payment_ids:
                    #         value_list.append((0, 0, {
                    #             'payment_term_id': each.id,
                    #         }))
                        # order.payment_term_ids.unlink()
                        # order.payment_term_ids = value_list

    @api.onchange('report_template_amc_id','report_template_amc_id_water','pool_type')
    def _onchange_report_template_amc_id(self):
        for order in self:
            report_name = order.report_template_amc_id.report_name if order.report_template_amc_id else ''
            order.is_amc_non_corporate = report_name == 'bi_amc_proposal.report_amc'
            order.is_amc_corporate = report_name == 'bi_amc_proposal.report_amc_corporate'

            if order.is_amc_corporate:
                # Clear corporate-specific fields
                order.update({
                    'amc_asset_details': [(5, 0, 0)],
                    'terms_condtion_corporate_ids': [(5, 0, 0)],
                    'specific_conditions_corporate_ids': [(5, 0, 0)],
                    'general_scope_corporate_ids': [(5, 0, 0)],
                    'detailed_scope_corporate_ids': [(5, 0, 0)],
                    'amc_scope_corporate_ids': [(5, 0, 0)],
                })

                # Fetch corporate-specific data
                corporate_template_details = self.env['corporate.template.details'].search([])
                terms_condition_master = self.env['amc.corporate.terms.conditions'].search([])
                specific_conditions_master = self.env['amc.corporate.specific.conditions'].search([])
                general_scope_master = self.env['amc.corporate.general.scope.work'].search([])
                detailed_scope_master = self.env['amc.corporate.detail.scope.work'].search([])
                amc_scope_master = self.env['amc.corporate.scope.work'].search([])

                # Prepare corporate data
                corporate_details = [
                    (0, 0, {
                        "sl_no": line.sl_no,
                        "name": line.name,
                        "asset_action": line.asset_action,
                    })
                    for corporate in corporate_template_details
                    for line in corporate.template_line_ids
                ]
                terms_conditions = [(0, 0, {'description': line.name}) for line in terms_condition_master]
                specific_conditions = [(0, 0, {'description': line.name}) for line in specific_conditions_master]
                general_scope = [(0, 0, {'description': line.name}) for line in general_scope_master]
                detailed_scope = [(0, 0, {'description': line.name}) for line in detailed_scope_master]
                amc_scope = [(0, 0, {'description': line.name}) for line in amc_scope_master]

                # Update corporate fields
                order.update({
                    'amc_asset_details': corporate_details,
                    'terms_condtion_corporate_ids': terms_conditions,
                    'specific_conditions_corporate_ids': specific_conditions,
                    'general_scope_corporate_ids': general_scope,
                    'detailed_scope_corporate_ids': detailed_scope,
                    'amc_scope_corporate_ids': amc_scope,
                })

            elif order.is_amc_non_corporate:
                # Clear non-corporate-specific fields
                order.update({
                    'terms_conditions_ids': [(5, 0, 0)],
                    'specific_conditions_ids': [(5, 0, 0)],
                    'general_scope_ids': [(5, 0, 0)],
                    'detailed_scope_ids': [(5, 0, 0)],
                    'amc_scope_ids': [(5, 0, 0)],
                })

                # Fetch non-corporate-specific data
                terms_condition_master = self.env['amc.non.corporate.terms.conditions'].search([])
                specific_conditions_master = self.env['amc.non.corporate.specific.conditions'].search([])
                general_scope_master = self.env['amc.non.corporate.general.scope.work'].search([])
                detailed_scope_master = self.env['amc.non.corporate.detail.scope.work'].search([])
                amc_scope_master = self.env['amc.non.corporate.scope.work'].search([])

                # Prepare non-corporate data
                terms_conditions = [(0, 0, {'description': line.name}) for line in terms_condition_master]
                specific_conditions = [(0, 0, {'description': line.name}) for line in specific_conditions_master]
                general_scope = [(0, 0, {'description': line.name}) for line in general_scope_master]
                detailed_scope = [(0, 0, {'description': line.name}) for line in detailed_scope_master]
                amc_scope = [(0, 0, {'description': line.name}) for line in amc_scope_master]

                # Update non-corporate fields
                order.update({
                    'terms_conditions_ids': terms_conditions,
                    'specific_conditions_ids': specific_conditions,
                    'general_scope_ids': general_scope,
                    'detailed_scope_ids': detailed_scope,
                    'amc_scope_ids': amc_scope,
                })


    def action_amc_proposal(self):
        if not self.pool_type:
            raise UserError("Please mention the pool type.")
        if self.pool_type == 'swimming_pool':
            if not self.report_template_amc_id:
                raise UserError("Please select an amc template for Swimming Pool.")
            if self.report_template_amc_id.report_name == 'bi_amc_proposal.report_amc':
                return self.env.ref('bi_amc_proposal.action_report_amc_proposal').report_action(self)
            elif self.report_template_amc_id.report_name == 'bi_amc_proposal.report_amc_corporate':
                return self.env.ref('bi_amc_proposal.action_report_amc_corporate_proposal').report_action(self)

        elif self.pool_type == 'water_feature':
            if not self.report_template_amc_id_water:
                raise UserError("Please select a report template for Water Feature.")
            if self.report_template_amc_id_water.report_name == 'bi_amc_proposal.report_water_feature_corporate':
                return self.env.ref('bi_amc_proposal.action_water_feature_non_corporate').report_action(self)

    def action_vas_proposal(self):
        if not self.report_template_id:
            raise UserError("Please select a report template to print.")

        if self.report_template_id.report_name == 'bi_amc_proposal.report_vas_proposal':
            return self.env.ref('bi_amc_proposal.action_report_vas_proposal').report_action(self)
        elif self.report_template_id.report_name == 'bi_amc_proposal.report_vas_proposal1':
            return self.env.ref('bi_amc_proposal.action_report_vas_proposal1').report_action(self)
        else:
            raise UserError("The selected report template is not configured properly.")

    def get_value_order_line(self, partner_id):
        value_after_backslash = 0
        if self.order_line:
            for each in self.order_line:
                description = each.name
                if "from" in description:
                    value_after_backslash = description.split("from")[1].strip()
                else:
                    value_after_backslash = None

            return value_after_backslash
        
    def get_service_property_location(self, partner_id):
        service_property_location = 0
        if self.order_line:
            for each in self.order_line:
                description = each.service_property_location
                if description:
                    service_property_location = description
                else:
                    service_property_location = None

            return service_property_location    
    
    def get_discount_value(self, partner_id):
        discount_amount = 0
        subtotal = 0
        if self.order_line:
                for line in self.order_line.filtered(lambda l:l.display_type != 'line_section' and l.product_template_id.name == 'Discount').mapped('price_subtotal'):
                    discount_amount = line
                for line in self.order_line.filtered(lambda l:l.display_type != 'line_section' and l.product_template_id.name != 'Discount').mapped('price_subtotal'):
                    subtotal += line
        return discount_amount,subtotal
    

class SaleOrder(models.Model):
    _inherit = 'sale.order.line'


    service_property_location=fields.Char(string="Service / Property / Location")

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    is_vas_report = fields.Boolean(string="Is VAS Report", help="Indicates if this report is a VAS-specific template.")
    is_swimming_template = fields.Boolean(string="Is Swimming Pool Template", help="Indicates if this report is a Swimming Pool Template")
    is_water_template = fields.Boolean(string="Is Water Feature Template", help="Indicates if this report is a Water Feature Template")

class CorporateTemplateDetails(models.Model):
    _name = 'corporate.template.details'
    _description = 'Corporate Template Details'

    name = fields.Char(string='Name')

    template_line_ids = fields.One2many(
        comodel_name='corporate.template.line',inverse_name='template_id',string='Template Lines')
    active = fields.Boolean(default=True)

class CorporateTemplateLine(models.Model):
    _name = 'corporate.template.line'
    _description = 'Corporate Template Line'

    name = fields.Char(string='Name')
    asset_action = fields.Char(string='Asset Action', store=True)
    sl_no = fields.Integer(string='Sl No',store=True)

    display_type = fields.Selection([('line_section', "Section")])

    template_id = fields.Many2one(
        comodel_name='corporate.template.details',
        string='Template',
        required=True,
    )

class AssetLine(models.Model):
    _name = 'asset.line'
    _description = 'Asset Line'

    name = fields.Char(string='Name')
    sl_no = fields.Integer(string='Sl No',store=True)
    asset_action = fields.Char(string='Asset Action', store=True)
    display_type = fields.Selection([
        ('line_section', "Section")
    ], string="Display Type")

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
    )
class Warranty(models.Model):
    _name = 'vas.warranty'
    _description = 'Warranty'

    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

class Exclusion(models.Model):
    _name = 'product.exclusion'
    _description = 'Exclusion'

    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)


class VasExclusionLine(models.Model):
    _name = 'vas.exclusion.line'
    _description = 'VAS Exclusion Line'

    order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Exclusion Description")
    active = fields.Boolean(default=True)

class VasWarrantyLine(models.Model):
    _name = 'vas.warranty.line'
    _description = 'VAS Warranty Line'

    order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Warranty Description")
    active = fields.Boolean(default=True)
    
class WarrantyExclutionLine(models.Model):
    _name = 'warranty.exclution.line'
    _description = 'Warranty Exclution Line'

    order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Warranty Exclution Description")
    active = fields.Boolean(default=True)
    
class AMCNonCorporateTermsAndConditions(models.Model):
    _name = 'delivery.period.line'
    _description = 'Delivery Period Line'

    order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Delivery Period Description")
    active = fields.Boolean(default=True)

class AMCNonCorporateTermsAndConditions(models.Model):
    _name = 'amc.non.corporate.terms.conditions'
    _description = 'AMC Non-Corporate Terms and Conditions'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

class AMCCorporateTermsAndConditions(models.Model):
    _name = 'amc.corporate.terms.conditions'
    _description = 'AMC Corporate Terms and Conditions'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

class AMCCorporateSpecificConditions(models.Model):
    _name = 'amc.corporate.specific.conditions'
    _description = 'AMC Corporate Specific Conditions'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

class AMCCorporateGeneralScopeofWork(models.Model):
    _name = 'amc.corporate.general.scope.work'
    _description = 'AMC Corporate General Scope of Work'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

class AMCCorporateDetailScopeofWork(models.Model):
    _name = 'amc.corporate.detail.scope.work'
    _description = 'AMC Corporate Detail Scope of Work'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

class AMCCorporateScopeofWork(models.Model):
    _name = 'amc.corporate.scope.work'
    _description = 'AMC Corporate Scope of Work'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

class AMCNonCorporateSpecificConditions(models.Model):
    _name = 'amc.non.corporate.specific.conditions'
    _description = 'AMC Non-Corporate Specific Conditions'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    
class AMCNonCorporateGeneralScopeofWork(models.Model):
    _name = 'amc.non.corporate.general.scope.work'
    _description = 'AMC Non-Corporate General Scope of Work'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    
class AMCNonCorporateDetailScopeofWork(models.Model):
    _name = 'amc.non.corporate.detail.scope.work'
    _description = 'AMC Non-Corporate Detail Scope of Work'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    
class AMCNonCorporateScopeofWork(models.Model):
    _name = 'amc.non.corporate.scope.work'
    _description = 'AMC Non Corporate Scope of Work'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)

class SaleOrderTermsConditions(models.Model):
    _name = 'sale.order.terms.conditions'
    _description = 'Sale Order Terms and Conditions'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")
    active = fields.Boolean(default=True)

class SaleOrderTermsConditionsCorporate(models.Model):
    _name = 'sale.order.terms.conditions.corporate'
    _description = 'Sale Order Terms and Conditions'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")
    active = fields.Boolean(default=True)

class SaleOrderSpecificConditions(models.Model):
    _name = 'sale.order.specific.conditions'
    _description = 'Sale Order Specific Conditions'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")
    active = fields.Boolean(default=True)

class SaleOrderSpecificConditionsCorporate(models.Model):
    _name = 'sale.order.specific.conditions.corporate'
    _description = 'Sale Order Specific Conditions'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")
    active = fields.Boolean(default=True)


class SaleOrderGeneralScope(models.Model):
    _name = 'sale.order.general.scope'
    _description = 'Sale Order General Scope of Work'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")

class SaleOrderGeneralScopeCorporate(models.Model):
    _name = 'sale.order.general.scope.corporate'
    _description = 'Sale Order General Scope of Work'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")


class SaleOrderDetailedScope(models.Model):
    _name = 'sale.order.detailed.scope'
    _description = 'Sale Order Detailed Scope of Work'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")

class SaleOrderDetailedScopeCorporate(models.Model):
    _name = 'sale.order.detailed.scope.corporate'
    _description = 'Sale Order Detailed Scope of Work'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")

class SaleOrderAmcScope(models.Model):
    _name = 'sale.order.amc.scope'
    _description = 'Sale Order AMC Scope of Work'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")

class SaleOrderAmcScopeCorporate(models.Model):
    _name = 'sale.order.amc.scope.corporate'
    _description = 'Sale Order AMC Scope of Work'

    sale_order_id = fields.Many2one('sale.order', string="Sale Order")
    description = fields.Text(string="Description")
    
class WarrantyExclusion(models.Model):
    _name = 'warranty.exclusion'
    _description = 'Warranty Exclusion'

    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

class DeliveryPeriod(models.Model):
    _name = 'delivery.period'
    _description = 'Delivery Period'

    description = fields.Text(string='Description')
    active = fields.Boolean(default=True)

class PaymentTermDetails(models.Model):
    _name = 'payment.term.details'
    _description = 'Payment Term Details'

    name = fields.Char(string='Name')
    active = fields.Boolean(string="Active", default=True)

    payment_line_ids = fields.One2many(
        comodel_name='payment.term.line',inverse_name='payment_term_id',string='Payment term Lines')

class PaymentTermLine(models.Model):
    _name = 'payment.term.line'
    _description = 'Payment Term Line'

    first_payment_percentage = fields.Float(string='First percentage')
    second_payment_percentage = fields.Float(string='Second percentage')


    payment_term_id = fields.Many2one(
        comodel_name='payment.term.details',
        string='Payment',
    )

class PaymenttLine(models.Model):
    _name = 'payment.line'
    _description = 'Payment Line'

    payment_term_id = fields.Many2one('payment.term.details',string="Payment Term")

    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
    )

class GeneralScopeofWork(models.Model):
    _name = 'scope.of.work'
    _description = 'General Scope of Work'
    _rec_name = 'description'

    description = fields.Char("Description")
    active = fields.Boolean(default=True)

class CompletionPeriodMaster(models.Model):
    _name = 'completion.period.master'
    _description = 'CompletionPeriodMaster'
    _rec_name = 'description'

    description = fields.Char("Description")
    active = fields.Boolean(default=True)

class CompletionPeriodLine(models.Model):
    _name = 'completion.period.line'
    _description = 'CompletionPeriodLine'

    description = fields.Char("Description")
    sale_order_id = fields.Many2one(
        comodel_name='sale.order',
        string='Sale Order',
    )


class VasPaymentTerms(models.Model):
    _name = 'vas.payment.terms'
    _description = 'Vas Payment Terms'
    _rec_name = "description"

    description = fields.Char(string='Description', required=True)
    active = fields.Boolean(default=True)