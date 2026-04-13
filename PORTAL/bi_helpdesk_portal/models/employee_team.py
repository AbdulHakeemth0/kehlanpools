from odoo import fields,models,api

class HrEmployeeTeam(models.Model):
    _name = 'hr.employee.team'
    _description = 'Employee Team'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char('Team', required=True)
    team_lead_id = fields.Many2one('hr.employee',string="Team Lead", domain=[("is_team_lead", "=", True)])
    members_ids = fields.Many2many('hr.employee', string="Members", store= True)


    @api.onchange("team_lead_id")
    def onchange_team_lead(self):
        if self.team_lead_id:
            self.members_ids = [(6,0,[self.team_lead_id.id])]
    
