from odoo import fields,models,api


class PasiCommision(models.Model):
    _name = "pasi.commission"
    _rec_name = "company_id"
    _description = "Passi Commission"
    
    employee_contribution = fields.Float(string="Employee Contribution", tracking=True)
    employer_contribution = fields.Float(string="Employer Contribution", tracking=True)
    company_id = fields.Many2one('res.company', string="Company", readonly=True, default=lambda self: self.env.company.id)

    @api.model
    def _valid_field_parameter(self, field, name):
        if name == 'tracking' and field.type == 'float':
            return True
        return super(PasiCommision, self)._valid_field_parameter(field, name)