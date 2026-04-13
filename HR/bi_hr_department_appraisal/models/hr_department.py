from odoo import fields, models

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    department_line_ids = fields.One2many('hr.department.line', 'department_id',string='Department Skill')


class HrDepartmentNoteLine(models.Model):
    _name = 'hr.department.line'
    _description ='Hr Department Line'

    department_id = fields.Many2one('hr.department', string='Department',required=True)
    skill_id  = fields.Many2one('hr.department.skill', string='Skill Name')