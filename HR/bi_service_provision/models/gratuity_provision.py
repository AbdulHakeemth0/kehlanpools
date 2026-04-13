from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools.date_utils import start_of, end_of
from datetime import date, timedelta,datetime
from dateutil.relativedelta import relativedelta 
import calendar


class GratuityProvision(models.Model):
    _name = "gratuity.provision"
    _description = "Gratuity Provision"
    _rec_name = 'employee_id'
    
    employee_id = fields.Many2one('hr.employee',string ="employee", domain = "['|', ('active', '=', True), ('active', '=', False)]")
    contract_state = fields.Selection(selection = [
        ('draft','New'),
        ('open','Running'),
        ('close','Expired'),
        ('cancel','Cancelled')
    ],string = "Contract State", tracking=True)
    gratuity_provision_line_ids = fields.One2many('gratuity.provision.line','gratuity_provision_id',string = "Gratuity provision line")

    @api.model
    def _valid_field_parameter(self, field, name):
        if name == 'tracking' and field.type == 'selection':
            return True
        return super(GratuityProvision, self)._valid_field_parameter(field, name)
    
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        for rec in self:
            employee = rec.employee_id
            if not employee:
                continue
            gratuity = self.env['gratuity.provision'].search([('employee_id', '=', employee.id)], limit=1)
            if gratuity and 'is_write' in gratuity._context and not gratuity._context['is_write']:
                raise ValidationError(_("Gratuity provision already exists for this employee."))
            contract = self.env['hr.contract'].sudo().search([
                ('employee_id', '=', employee.id),
                ('state', 'in', ['open', 'close'])], order='date_start desc', limit=1)
            if not contract:
                continue
            rec.gratuity_provision_line_ids = False
            start_date = employee.joining_date
            current_date = datetime.now()
            total_years = current_date.year - start_date.year + 1
            lines = []
            for i in range(total_years):
                year_date = start_date + relativedelta(years=i)
                experience = i
                if i == 0:
                    amount = 0
                elif i <= 3:
                    amount = contract.wage / 2
                else:
                    amount = contract.wage
                lines.append((0, 0, {
                    'year': year_date,
                    'experience': experience,
                    'amount': amount,
                }))

            rec.gratuity_provision_line_ids = lines
        

class GratuityProvisionLine(models.Model):
    _name = "gratuity.provision.line"
    _description = "Gratuity Provision Line" 
    
    year = fields.Date(string = "year")
    experience = fields.Integer(string = "Experience")
    amount = fields.Float(string = 'Amount')  
    gratuity_provision_id = fields.Many2one('gratuity.provision',string = "Gratuity provision") 