from odoo import models, fields, api
import base64


class ResPartner(models.Model):
    _inherit = 'res.partner'


    def send_followup_email(self, options):
        self.ensure_one()
        if  self.followup_status == 'in_need_of_action' and self.followup_reminder_type == 'automatic':
            wizard = self.env['account.statement.wizard'].create({
                'partner_id': self.id,
                'date': fields.Date.today(),
            })

            data = wizard._prepare_statement()
            report = self.env.ref("bi_partner_statement_of_account.action_report_account_followup_new")
            data.update({
                "account_type": self.property_account_receivable_id.account_type if self.customer_rank > 0 else 'liability_payable',
            })
            pdf_content, _ = report._render_qweb_pdf(report.id, data=data)

            attachment = self.env['ir.attachment'].create({
                'name': f"Account Statement - {self.name}.pdf",
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': 'account_followup.manual_reminder',
                'res_id': False,  
                'mimetype': 'application/pdf'
            })            
            # self.followup_line_id.mail_template_id.attachment_ids = [(4, attachment.id)]
            options['attachment_ids'] = [attachment.id]

        return super(ResPartner, self).send_followup_email(options)
