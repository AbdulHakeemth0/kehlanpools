from odoo import models, fields, api, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta


class AmcPlan(models.Model):
    _name = 'amc.plan'
    _description = 'AMC Plan'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="AMC", copy=False, default=lambda self: _('New'))
    services_involved = fields.Many2many('product.product', string="Services Involved", tracking=True)
    customer_id = fields.Many2one('res.partner', string="Customer")
    invoice_count = fields.Integer(string="Invoice Count", compute='_compute_get_invoices')
    amc_history_count = fields.Integer(compute='_compute_get_amc')
    invoice_disable = fields.Boolean(string="Invoice Disable")
    recurring_interval_type = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Period", tracking=True)
    recurring_interval = fields.Integer(string="Duration", default=1, tracking=True)
    recurring_period = fields.Integer(string="Duration  ", default=1)
    start_date = fields.Date(string="Start Date", default=fields.Date.context_today, tracking=True)
    next_maintenance_date = fields.Date(string="Next Maintenance Date", compute="_compute_next_maintenance", store=True)
    # end_date = fields.Date(string="End Date", compute="_compute_end_date", store=True)
    end_date = fields.Date(string="End Date", tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('cancel', 'Cancel'),
        ('expired', 'Expired')
    ], string="Status", default='draft')
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', copy=False)
    # invoice_id = fields.Many2one('account.move', string="Invoice :", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals['sale_order_id']:
                sale_id = self.env['sale.order'].search([('id', '=', vals['sale_order_id'])])
                sale_id.action_confirm()
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = (self.env['ir.sequence'].next_by_code('amc.plan'))
        return super().create(vals_list)

    def action_view_button(self):
        self.ensure_one()
        domain = [('amc_plan_id', '=', self.id)]
        return {
            'name': 'AccountMove',
            'view_mode': 'list,form',
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain': domain,
            'target': 'current',
        }

    @api.model
    def _compute_get_invoices(self):
        for record in self:
            record.invoice_count = self.env['account.move'].search_count([('amc_plan_id', '=', record.id)])

    @api.depends('start_date', 'recurring_interval', 'recurring_interval_type')
    def _compute_next_maintenance(self):
        for record in self:
            if record.start_date and record.recurring_interval:
                if record.recurring_interval_type == 'days':
                    record.next_maintenance_date = record.start_date + timedelta(days=record.recurring_interval)
                elif record.recurring_interval_type == 'weeks':
                    record.next_maintenance_date = record.start_date + timedelta(weeks=record.recurring_interval)
                elif record.recurring_interval_type == 'months':
                    record.next_maintenance_date = record.start_date + relativedelta(months=record.recurring_interval)
                elif record.recurring_interval_type == 'years':
                    record.next_maintenance_date = record.start_date + relativedelta(years=record.recurring_interval)

    # @api.depends('start_date', 'recurring_period', 'recurring_interval_type')
    # def _compute_end_date(self):
    #     for record in self:
    #         if record.start_date and record.recurring_period:
    #             if record.recurring_interval_type == 'days':
    #                 record.end_date = record.start_date + timedelta(days=record.recurring_period)
    #             elif record.recurring_interval_type == 'weeks':
    #                 record.end_date = record.start_date + timedelta(weeks=record.recurring_period)
    #             elif record.recurring_interval_type == 'months':
    #                 record.end_date = record.start_date + relativedelta(months=record.recurring_period)
    #             elif record.recurring_interval_type == 'years':
    #                 record.end_date = record.start_date + relativedelta(years=record.recurring_period)

    def activate_plan(self):
        self.state = 'active'

    @api.model
    def _compute_get_amc(self):
        for rec in self:
            records = self.env["amc.plan"].search([("sale_order_id", "=", rec.sale_order_id.id)])
            rec.amc_history_count = len(records)

    def view_existing_amc(self):
        return {
            "name": "AMC History",
            "type": "ir.actions.act_window",
            "res_model": "amc.plan", 
            "view_mode": "list,form",
            "domain": [("sale_order_id", "=", self.sale_order_id.id)]
        }

    def renew_contract(self):
        new_amc_plan = self.env['amc.plan'].create({
            'customer_id': self.customer_id.id,
            'services_involved': [(6, 0, self.services_involved.ids)],
            'start_date': fields.Date.today(),
            'sale_order_id': self.sale_order_id.id,
        })
        context = {
            'default_customer_id': self.customer_id.id,
            'default_services_involved': self.services_involved.ids,
            'default_start_date': fields.Date.today(),
            'default_sale_order_id': self.sale_order_id.id,
        }
        return {
            'name': "AMC Renewal Contract",
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'amc.plan',
            'res_id': new_amc_plan.id,
            'target': 'current',
            'context': context,
        }


    def cancel_plan(self):
        self.state = 'cancel'

    def expire_plan(self):
        self.state = 'expired'

    def create_invoice(self):
        if not self.state in ['cancel', 'expired']:
            today = fields.Date.today()
            invoice_lines = []
            for task in self.services_involved:
                line_vals = {
                    'product_id': task.id, 
                    'name': self.name,
                    'quantity': 1,
                }
                invoice_lines.append((0, 0, line_vals))
            
            invoice_vals = {
                'partner_id': self.customer_id.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.context_today(self),
                'amc_plan_id': self.id,
                'invoice_line_ids': invoice_lines,
            }
            
            self.env['account.move'].create(invoice_vals)

            task_vals = {
                'name': self.name,
                'project_id':3,
                'partner_id': self.customer_id.id if self.customer_id else False,
                'date_deadline': self.next_maintenance_date,
            }
            self.env['project.task'].create([task_vals])

            # self.invoice_id = invoice.id
            self.invoice_disable = True 

            if today == self.end_date:
                self.state = 'expired'
            else:
                self.state = 'active'

            return 
        
    @api.model
    def action_cron_auto_create_invoice(self):
        today = fields.Date.today()
        maintenance_invoice = self.search([
            ('state', '=', 'active'),
            ('state', '!=', 'cancel'),
            ('state', '!=', 'expired'),
            ('next_maintenance_date', '=', today),
            ('end_date', '>=', today),
        ])  
        for each in maintenance_invoice:
            each.create_invoice()
            each._compute_next_maintenance()  


class AccountMove(models.Model):
    _inherit = "account.move"

    amc_plan_id = fields.Many2one('amc.plan')
