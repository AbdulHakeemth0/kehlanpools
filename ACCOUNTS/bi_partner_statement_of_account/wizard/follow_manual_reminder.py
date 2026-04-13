from odoo import api, fields, models, Command
import base64

class FollowupManualReminder(models.TransientModel):
    _inherit = 'account_followup.manual_reminder'

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        assert self.env.context['active_model'] == 'res.partner'
        partner = self.env['res.partner'].browse(self.env.context['active_ids'])
        partner.ensure_one()
        followup_line = partner.followup_line_id
        
        if followup_line:
            defaults.update(
                email=followup_line.send_email,
                sms=followup_line.send_sms,
                template_id=followup_line.mail_template_id.id,
                sms_template_id=followup_line.sms_template_id.id,
                join_invoices=followup_line.join_invoices,
            )

        wizard = self.env['account.statement.wizard'].create({
            'partner_id': partner.id,
            'date': fields.Date.today(),
        })

        data = wizard._prepare_statement()
        report = self.env.ref("bi_partner_statement_of_account.action_report_account_followup_new")
        data.update({
            "account_type": partner.property_account_receivable_id.account_type if partner.customer_rank > 0 else 'liability_payable',
        })
        pdf_content, _ = report._render_qweb_pdf(report.id, data=data)

        attachment = self.env['ir.attachment'].create({
            'name': f"Account Statement - {partner.name}.pdf",
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'account_followup.manual_reminder',
            'res_id': False,  
            'mimetype': 'application/pdf'
        })

        defaults.update(
            partner_id=partner.id,
            email_recipient_ids=[Command.set((partner._get_all_followup_contacts() or partner).ids)],
            attachment_ids=[Command.set(partner._get_included_unreconciled_aml_ids().move_id.message_main_attachment_id.ids)] + [(4, attachment.id)], 
        )

        return defaults