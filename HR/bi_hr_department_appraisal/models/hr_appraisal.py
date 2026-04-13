from odoo import api, fields, models, _

class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'
  
    employee_appraisal_skill_line_ids = fields.One2many('hr.appraisal.skill.line','employee_appraisal_id',string="Dept. Lines")
    is_dept_skills_passed = fields.Boolean(string="Skills Passed", compute="_compute_is_dept_skills_passed")
    salary_inc = fields.Float(string="Salary Increment")

    def _compute_is_dept_skills_passed(self):
        for each in self:
            self.employee_appraisal_skill_line_ids.unlink()
            if each.department_id:
                skills = each.department_id.department_line_ids
                if skills:
                    skill_lines = []
                    for skill in skills:
                        skill_lines.append((0, 0, {
                            'skill_id': skill.skill_id.id,
                        }))
                    each.employee_appraisal_skill_line_ids = skill_lines
                    each.is_dept_skills_passed = True
                else:
                    each.is_dept_skills_passed = False
            else:
                each.is_dept_skills_passed = False
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        for each in self:
            if each.employee_id:
                if each.department_id:
                    each._compute_is_dept_skills_passed()

class HrAppraisakSkillLine(models.Model):
    _name = 'hr.appraisal.skill.line'
    _description = 'HR Appraisal Skill Lines'


    employee_appraisal_id = fields.Many2one('hr.appraisal', string="Employee")
    rating_scale = fields.Selection(
        [('poor', 'Poor'),
         ('fair', 'Fair'),
         ('good', 'Good'),
         ('very_good', 'Very Good'),
         ('excellent', 'Excellent')],
        string="Rating Scale"
    )
    skill_id = fields.Many2one('hr.department.skill' ,string="Skills")