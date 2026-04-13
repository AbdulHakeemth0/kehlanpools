from odoo import api, fields, models, _


class HelpdeskTicketConvert2Lead(models.TransientModel):
    _inherit = "helpdesk.ticket.to.lead"


    def action_convert_to_lead(self):
        res = super(HelpdeskTicketConvert2Lead, self).action_convert_to_lead()
        for rec in self:
            lead = self.env[res['res_model']].browse(res['res_id'])
            lead.ticket_id = rec.ticket_id.id
            users = self.env.ref('bi_helpdesk_portal.help_desk_manager_id').users
            mail_users = self.env['hr.employee'].sudo().search([]).filtered(lambda l:l.job_id.is_operational_manager).user_id
            users += mail_users
            for user in users:
                model = self.env["ir.model"].sudo().search([("model", "=", "helpdesk.ticket")],limit=1)  
                data = {
                    "res_id": rec.ticket_id.id,
                    "res_model_id": model.id,
                    "user_id": user.id,
                    "summary": f"An opportunity have been created from the ticket {rec.ticket_id.name}.",
                    "activity_type_id": self.env.ref("bi_helpdesk_portal.opportunity_notify_activity_id").id
                }
                self.env["mail.activity"].sudo().create(data)

            # outgoing_mail_server = self.env['ir.mail_server'].search([], limit=1)
            # email_from = outgoing_mail_server.smtp_user if outgoing_mail_server else self.env.user.email_formatted
            # for email in mail_users: 
            #     main_content = {
            #         'subject': f"An opportunity have been created from the ticket {rec.ticket_id.name}.",
            #         'email_from': email_from,
            #         'body_html': f"An opportunity have been created from the ticket {rec.ticket_id.name}.",
            #         'email_to': email.login,
            #     }
            #     self.env['mail.mail'].create(main_content).send()
        return res