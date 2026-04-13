from odoo import models, fields


class CrmLead(models.Model):
    _inherit = "crm.lead"


    ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket')

    def _prepare_opportunity_quotation_context(self):
        res = super(CrmLead, self)._prepare_opportunity_quotation_context()
        if res:
            res["default_ticket_id"] = self.ticket_id.id
        return res