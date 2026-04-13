# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, Command, fields, models, _

class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"


    unassigned_tickets = fields.Integer(string='Unassigned Tickets', compute='_compute_unassigned_tickets')

    # override in this function 6/5/2025
    def _compute_unassigned_tickets(self):
        ticket_data = self.env['helpdesk.ticket']._read_group([
            ('team_lead_id', '=', False),  # change to in this line
            ('team_id', 'in', self.ids),
            ('stage_id.fold', '=', False),
        ], ['team_id'], ['__count'])
        mapped_data = {team.id: count for team, count in ticket_data}
        for team in self:
            team.unassigned_tickets = mapped_data.get(team.id, 0)