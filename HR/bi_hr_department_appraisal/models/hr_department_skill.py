from odoo import api, fields, models, _

class HrDepartmentSkill(models.Model):
    _name = 'hr.department.skill'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'HR Department Skill'

    name = fields.Char(string='Name')