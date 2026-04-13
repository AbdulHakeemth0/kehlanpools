from datetime import datetime, date, timedelta
from odoo import api, fields, models, _


class HrEmployeeDocument(models.Model):
    """Create a new module for retrieving document files, allowing users
     to input details about the documents."""
    _name = 'hr.employee.document'
    _description = 'HR Employee Documents'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(string='Document Number', required=True, copy=False,
                       help="Enter Document Number", tracking=True)
    document_id = fields.Many2one('employee.checklist',
                                  string='Document',
                                  required=True,
                                  help="Choose Employee Checklist for"
                                       " Employee Document", tracking=True)
    description = fields.Text(string='Description', copy=False,
                              help="Description for Employee Document")
    expiry_date = fields.Date(string='Expiry Date', copy=False,
                              help="Choose Expiry Date for Employee Document")
    employee_id = fields.Many2one('hr.employee', copy=False, string="Employee",
                                  help="Choose Employee for Employee Document")
    # doc_attachment_ids = fields.Many2many('ir.attachment',
    #                                       'doc_attach_ids',
    #                                       'doc_id', 'attach_id3',
    #                                       string="Attachment",
    #                                       help='You can attach the copy'
    #                                            'of your document',
    #                                       copy=False, tracking=True)
    doc_attachment_ids = fields.Many2many(
                        'ir.attachment',
                        'doc_attachment_ids',  # Table name
                        'doc_id', 'attach_id3',  # Column names
                        string="Attachment",
                        help='You can attach the copy of your document',
                        copy=False,
                        tracking=True
                    )
    issue_date = fields.Date(string='Issue Date',
                             default=fields.Date.context_today, copy=False,
                             help="Choose Issue Date for Employee Document", tracking=True)

    def mail_reminder(self):
        """Function for scheduling emails to send reminders
        about document expiry dates."""
        for doc in self.search([]):
            if doc.expiry_date:
                if (datetime.now() + timedelta(days=1)).date() >= (
                        doc.expiry_date - timedelta(days=7)):
                    mail_content = ("  Hello  " + str(
                        doc.employee_id.name) + ",<br>Your Document " + str(
                        doc.name) + " is going to expire on " + \
                                    str(doc.expiry_date) + ". Please renew it "
                                                           "before expiry date.")
                    main_content = {
                        'subject': _('Document-%s Will Expire On %s') % (
                            str(doc.name), str(doc.expiry_date)),
                        'author_id': self.env.user.partner_id.id,
                        'body_html': mail_content,
                        'email_to': doc.employee_id.work_email,
                    }
                    self.env['mail.mail'].create(main_content).send()
                    
                    # Notifiy employee's HR
                    if doc.employee_id.contract_id.hr_responsible_id:
                        model = self.env["ir.model"].sudo().search([("model", "=", "hr.employee.document")])
                        user = doc.employee_id.contract_id.hr_responsible_id
                        data = {
                            'res_id': doc.id,
                            'res_model_id': model.id,
                            'user_id': user.id,
                            'summary':_(('Document-%s Will Expire On %s') % (
                                str(doc.name), str(doc.expiry_date))),
                            "activity_type_id": self.env.ref("employee_documents_expiry.send_emp_doc_exp_activity").id,
                        }
                        self.env["mail.activity"].sudo().create(data)

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
