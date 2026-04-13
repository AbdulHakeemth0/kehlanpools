# Part of Odoo. See LICENSE file for full copyright and licensing details.
from dateutil import relativedelta

from odoo import api, Command, fields, models, _
from odoo.exceptions import ValidationError,UserError



class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    ticket_type = fields.Selection([
        ('service', 'Service'),
        ('maintenance', 'Maintenance'),
        ('complaint', 'Complaint'),
        ('corrective_maintenance', 'CM - Corrective Maintenance'),
        ('planned_preventive_maintenance', 'PPM - Planned Preventive Maintenance'),
        ('reactive_maintenance', 'RM - Reactive Maintenance'),
        ('customer_complaints', 'CC- Customer Complaints'),
        ('planned_management_escalation', 'CME - Customer Management Escalation'),
        ('project_related_complaints', 'PRC - Project Related Complaints'),
        ('under_warranty', 'Under Warranty')
    ], string="Type", required=True)
    mem_ids = fields.Many2many('hr.employee',compute="_compute_mem_id_domain")
    members_ids = fields.Many2many('hr.employee', string="Members") 
    is_opportunity = fields.Boolean(compute="_compute_opportunity")
    team_lead_id = fields.Many2one('hr.employee',string="Assigned To",domain=lambda self: self._get_team_lead_domain())
    is_assigned = fields.Boolean(string="Is assigned")
    deadline = fields.Selection(
        [("hours", "Hours"), ("date", "Date")],
        string="Deadline",
    )
    hours = fields.Float(string="Hours")
    date = fields.Date(string="Date")
    remarks = fields.Text(string="Remarks")
    cutomer_m_number = fields.Char(string="M-number")
    lead_count = fields.Integer(string="Lead Count", compute="_compute_lead_count")
    order_count = fields.Integer(string="Order Count", compute="_compute_order_count")

    def _compute_lead_count(self):
        for rec in self:
            lead_count = self.env['crm.lead'].search_count([('ticket_id', '=', rec.id)])
            rec.lead_count = lead_count or 0

    def _compute_order_count(self):
        for rec in self:
            order_count = self.env['sale.order'].search_count([('ticket_id','=',rec.id)])
            rec.order_count = order_count or 0 

    @api.onchange('cutomer_m_number')
    def onchange_cutomer_m_number(self):
        if self.cutomer_m_number:
            customer_id = self.env['res.partner'].search([('customer_rank', '!=', 0),('code', 'ilike', self.cutomer_m_number)])
            for each in customer_id:
                if each:
                    self.partner_id = each.id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            self.cutomer_m_number = self.partner_id.code

    @api.model
    def _get_team_lead_domain(self):
        team_leads = self.env['hr.employee'].sudo().search([('is_team_lead', '=', True)])
        return [('id', 'in', team_leads.ids)]

    @api.depends('team_lead_id')
    def _compute_mem_id_domain(self):
        for each in self:
            mems_ids = []
            if each.team_lead_id:
                team_id = self.env['hr.employee.team'].search([('team_lead_id', '=', each.team_lead_id.id)])
                if team_id:
                    for each_mem in team_id.members_ids:
                        mems_ids.append(each_mem.id)
                each.mem_ids = mems_ids
            else:
                mems_ids = []
                each.mem_ids = mems_ids

    @api.depends('partner_id')
    def _compute_opportunity(self):
        for each in self:
            if each.partner_id:
                customer_data = self.env['res.partner'].search([('id','=',each.partner_id.id)]).opportunity_ids
                if customer_data:
                    each.is_opportunity=True
                else:
                    each.is_opportunity=False
            else:
                each.is_opportunity=False

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HelpdeskTicket, self).create(vals_list)
        for vals in vals_list:
            users = self.env.ref('bi_helpdesk_portal.help_desk_manager_id').users
            for each_user in users:
                usr_id = each_user
                model = self.env["ir.model"].sudo().search([("model", "=", "helpdesk.ticket")])     
                data = {
                    "res_id": res.id,
                    "res_model_id": model.id,
                    "user_id": usr_id.id,
                    "summary": "Ticket request generated",
                    "activity_type_id": self.env.ref("bi_helpdesk_portal.help_desk_activity_id").id
                }
                self.env["mail.activity"].sudo().create(data) 
        return res

    def action_assign(self):
        if not self.team_lead_id:
            raise UserError(_("Please select team lead!!!"))
        if self.team_lead_id.user_id:
            usr_id = self.team_lead_id.user_id.id
            model = self.env["ir.model"].sudo().search([("model", "=", "helpdesk.ticket")])     
            data = {
                "res_id": self.id,
                "res_model_id": model.id,
                "user_id": usr_id,
                "summary": f"{self.name}-ticket has been assigned to you.",
                "activity_type_id": self.env.ref("bi_helpdesk_portal.help_desk_activity_id").id
            }
            self.env["mail.activity"].sudo().create(data)
        self.stage_id = self.env['helpdesk.stage'].search([('is_assign','=',True)])
        self.is_assigned = True

    def action_get_opportunity(self):
        return {
            "name": ("Leads"),
            "res_model": "crm.lead",
            # 'res_id':requisition_id.id,
            "view_mode": "list,form",
            "type": "ir.actions.act_window",
            "domain": [("ticket_id", "=", self.id)],
            "target": "current",
        }

    def action_get_sale_order(self):
        return {
            "name": "Sale Order",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "sale.order",
            "domain": [("ticket_id", "=", self.id)],
            "target": "current",
        }
    
    #Server action function:
    def action_assign_created_by_to_assigned_to(self):
        for record in records:
            record.write({'user_id': record.create_uid.id})
