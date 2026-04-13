from datetime import datetime, date, timedelta
from odoo import api, fields, models, _

class VehicleDocument(models.Model):
    _name = 'vehicle.document'
    _description = 'vehicle document'
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string='Document Number', required=True, copy=False, help="Enter Document Number", tracking=True)
    description = fields.Text(string='Description', copy=False, help="Description for Vehicle Document", tracking=True)
    expiry_date = fields.Date(string='Expiry Date', copy=False, help="Choose Expiry Date for Vehicle Document", tracking=True)
    vehicle_id = fields.Many2one('fleet.vehicle', copy=False, string="Vehicle", help="Choose Vehicle for Vehicle Document")
    # doc_attachment_ids = fields.Many2many('ir.attachment',
    #                                       'doc_attachment_ids',
    #                                       'doc_id', 'attach_id2',
    #                                       string="Attachment",
    #                                       tracking=True,
    #                                       help='You can attach the copy of your document',
    #                                       copy=False)
    doc_attachment_ids = fields.Many2many('ir.attachment',
                                            string="Attachment",
                                            tracking=True,
                                            help='You can attach the copy of your document',
                                            copy=False
)
    issue_date = fields.Date(string='Issue Date',default=fields.Date.context_today, tracking=True, copy=False, help="Choose Issue Date for Vehicle Document")

    def fleet_doc_mail_reminder(self):
        employees = self.env['hr.employee'].sudo().search([('job_id.is_fleet_visible', '=', True)])
        work_mails = employees.mapped('work_email')
        outgoing_mail_server = self.env['ir.mail_server'].search([], limit=1)
        email_from = outgoing_mail_server.smtp_user if outgoing_mail_server else self.env.user.email_formatted
        for doc in self.search([]):
            if doc.expiry_date:
                if (datetime.now() + timedelta(days=1)).date() >= (doc.expiry_date - timedelta(days=7)):
                    mail_content = (
                        f"Hello,<br>Your Document {doc.name} is going to expire on {doc.expiry_date}. "
                        "Please renew it before the expiry date."
                    )
                    for email in work_mails: 
                        main_content = {
                            'subject': _('Document-%s Will Expire On %s') % (str(doc.name), str(doc.expiry_date)),
                            'email_from': email_from,
                            # 'author_id': self.env.user.partner_id.id,
                            'body_html': mail_content,
                            'email_to': email,
                        }
                        self.env['mail.mail'].create(main_content).send()

    @api.onchange('expiry_date')
    def check_expr_date(self):
        """Function to obtain a validation error for expired documents."""
        if self.expiry_date and self.expiry_date < date.today():
            return {
                'warning': {
                    'title': _('Document Expired.'),
                    'message': _("Your Document Is Already Expired.")
                }
            }
