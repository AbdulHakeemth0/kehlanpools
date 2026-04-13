from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import email_split
import logging

_logger = logging.getLogger(__name__)


class PettyCashRequest(models.Model):
    _name = 'petty.cash.request'
    _description = 'Petty Cash Request'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = 'request_number'

    request_number = fields.Char(string='Petty Cash No.', readonly=True, default='New', copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        # ('manager_approval', 'Manager Approval'),
        ('coo_approval', 'COO Approval'),
        ('ceo_approval', 'CEO Approval'),
        ('approved','Approved'),
        ('reject','Rejected')
    ], default='draft', tracking=True)

    line_ids = fields.One2many('petty.cash.line', 'cash_request_id', string='Expense Lines')
    total_amount = fields.Float(string='Total Amount', compute='_compute_total', store=True)
    statement_no = fields.Char(
        string='Statement No.',
    )
    narration = fields.Text(
        string='Narration',
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company.id,
    )
    requested_date = fields.Date(
        string='Requested date',
        default=fields.Date.context_today,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        ondelete="restrict",
        default=lambda self: self.env.user.company_id.currency_id,
    )
    prepared_by = fields.Char("Prepared By")
    received_by = fields.Char("COO")
    approval1_name = fields.Char("First Approver Name")
    approval2_name = fields.Char("CEO")
    approval1 = fields.Selection([
        ('finance', 'Finance Manger'),
        ('general', 'General Manager'),
        # ('coo', 'Chief Operating Officer'),
        # ('ceo', 'Chief executive Officer'),
    ], string="First Approval")
    approval2 = fields.Selection([
        ('finance', 'Finance Manger'),
        ('general', 'General Manager'),
        ('coo', 'Chief Operating Officer'),
        ('ceo', 'Chief executive Officer'),
    ], string="Second Approval")
    
    reject_reason = fields.Text(
        string='Reject Reason',
    )
    
    @api.model
    def create(self, vals):
        if vals.get('request_number', 'New') == 'New':
            vals['request_number'] = self.env['ir.sequence'].next_by_code('petty.cash.request')
        return super().create(vals)

    @api.depends('line_ids.amount', 'line_ids.rejected')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(
                line.amount for line in rec.line_ids if not line.rejected
            )
            
    def action_approve_request(self):
        for rec in self:
            if not rec.line_ids:
                raise UserError(_("Please add at least one expense line before requesting approval."))

            employees = self.env['hr.employee'].sudo().search([('job_id.is_coo', '=', True)])
            if not employees:
                raise ValidationError(_("There is no employee which matches the COO position."))

            server = self.env['ir.mail_server'].sudo().search([], order='sequence asc', limit=1)
            if not server:
                raise ValidationError(_("No outgoing mail server configured."))

            # Deep link to this record
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            action = self.env.ref('your_module.action_petty_cash_request', raise_if_not_found=False)
            action_part = f"&action={action.id}" if action else ""
            record_url = f"{base_url}/web#id={rec.id}&model=petty.cash.request&view_type=form{action_part}"

            # Email HTML
            body_html = f"""
                <div style="font-family:Arial, sans-serif; font-size:14px; color:#111;">
                    <p>A petty cash request has been sent by <b>{rec.env.user.name}</b>.</p>
                    <p>Please review and approve it:</p>
                    <p>
                        <a href="{record_url}"
                           style="background:#1f6feb;color:#ffffff;padding:10px 16px;border-radius:6px;
                                  text-decoration:none;display:inline-block;font-weight:600;">
                            Open Request in Odoo
                        </a>
                    </p>
                    <p style="color:#555;margin-top:12px;">If you’re not signed in, you’ll be prompted to log in first.</p>
                </div>
            """

            # Collect recipient emails (work_email first, fallback to user partner email)
            raw_emails = []
            for emp in employees:
                if emp.work_email:
                    raw_emails.append(emp.work_email)
                elif emp.user_id and emp.user_id.partner_id and emp.user_id.partner_id.email:
                    raw_emails.append(emp.user_id.partner_id.email)
            recipients = list({e.lower() for e in raw_emails if e})
            if not recipients:
                raise ValidationError(_("No recipient emails found for COO employees. Set a work email or user partner email."))

            # Subject
            subject = f"Petty Cash Request from {rec.env.user.name}"

            # Create a one-off template
            tmpl = self.env['mail.template'].sudo().create({
                'name': 'Petty Cash Approval (One-off)',
                'model_id': self.env['ir.model']._get_id('petty.cash.request'),
                'subject': subject,
                'body_html': body_html,
                'email_from': server.smtp_user or self.env.user.email_formatted,
                'mail_server_id': server.id,
            })

            # Send mails
            Mail = self.env['mail.mail'].sudo()
            sent_to, errors = [], []
            for email in recipients:
                try:
                    tmpl.with_context(mail_notify_force_send=True).send_mail(
                        rec.id,
                        force_send=True,
                        email_values={'email_to': email, 'auto_delete': False},
                    )
                except Exception as e:
                    errors.append(f"{email}: {e}")
                    continue

                mm = Mail.search([('email_to', 'ilike', email), ('subject', '=', subject)], order='id desc', limit=1)
                if mm and mm.state == 'exception':
                    errors.append(f"{email}: {mm.failure_reason or 'Unknown failure'}")
                elif mm and mm.state in ('sent', 'done'):
                    sent_to.append(email)

            # Log a summary in chatter
            summary_lines = [f"Recipients: {', '.join(recipients)}"]
            if sent_to:
                summary_lines.append("✅ Sent to: " + ", ".join(sent_to))
            if errors:
                summary_lines.append("❌ Errors:\n- " + "\n- ".join(errors))

            rec.message_post(
                body="<pre>%s</pre>" % ("\n".join(summary_lines)),
                subject="Petty Cash Email Send Summary",
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            # Move to COO approval state
            rec.write({'state': 'coo_approval'})

    def action_ceo_approve_request(self):
        for rec in self:
            employees = self.env['hr.employee'].sudo().search([('job_id.is_ceo', '=', True)])
            if not employees:
                raise ValidationError(_("There is no employee which matches the CEO position. Please enable the check box for the CEO position in the Job Position...!"))

            # Outgoing mail server
            server = self.env['ir.mail_server'].sudo().search([], order='sequence asc', limit=1)
            if not server:
                raise ValidationError(_("No outgoing mail server configured."))

            # Deep link to this record
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            action = self.env.ref('your_module.action_petty_cash_request', raise_if_not_found=False)
            action_part = f"&action={action.id}" if action else ""
            record_url = f"{base_url}/web#id={rec.id}&model=petty.cash.request&view_type=form{action_part}"

            # Email HTML
            body_html = f"""
                <div style="font-family:Arial, sans-serif; font-size:14px; color:#111;">
                    <p>A petty cash request has been sent by <b>{rec.env.user.name}</b>.</p>
                    <p>Please review and approve it:</p>
                    <p>
                        <a href="{record_url}"
                           style="background:#1f6feb;color:#ffffff;padding:10px 16px;border-radius:6px;
                                  text-decoration:none;display:inline-block;font-weight:600;">
                            Open Request in Odoo
                        </a>
                    </p>
                    <p style="color:#555;margin-top:12px;">
                        If you’re not signed in, you’ll be prompted to log in first.
                    </p>
                </div>
            """

            # Collect CEO emails
            raw_emails = []
            for emp in employees:
                if emp.work_email:
                    raw_emails.append(emp.work_email)
                elif emp.user_id and emp.user_id.partner_id and emp.user_id.partner_id.email:
                    raw_emails.append(emp.user_id.partner_id.email)
            recipients = list({e.lower() for e in sum([email_split(x) for x in raw_emails], []) if e})
            if not recipients:
                raise ValidationError(_("No recipient emails found for CEO employees."))

            # Subject
            subject = f"Petty Cash Request from {rec.env.user.name}"

            # Create template
            tmpl = self.env['mail.template'].sudo().create({
                'name': 'Petty Cash CEO Approval (One-off)',
                'model_id': self.env['ir.model']._get_id('petty.cash.request'),
                'subject': subject,
                'body_html': body_html,
                'email_from': server.smtp_user or self.env.user.email_formatted,
                'mail_server_id': server.id,
            })

            # Send mails
            Mail = self.env['mail.mail'].sudo()
            sent_to, errors = [], []
            for email in recipients:
                try:
                    tmpl.with_context(mail_notify_force_send=True).send_mail(
                        rec.id,
                        force_send=True,
                        email_values={'email_to': email, 'auto_delete': False},
                    )
                except Exception as e:
                    errors.append(f"{email}: {e}")
                    continue

                mm = Mail.search([('email_to', 'ilike', email), ('subject', '=', subject)], order='id desc', limit=1)
                if mm and mm.state == 'exception':
                    errors.append(f"{email}: {mm.failure_reason or 'Unknown failure'}")
                elif mm and mm.state in ('sent', 'done'):
                    sent_to.append(email)

            # Log summary in chatter
            summary_lines = [f"Recipients: {', '.join(recipients)}"]
            if sent_to:
                summary_lines.append("✅ Sent to: " + ", ".join(sent_to))
            if errors:
                summary_lines.append("❌ Errors:\n- " + "\n- ".join(errors))

            rec.message_post(
                body="<pre>%s</pre>" % ("\n".join(summary_lines)),
                subject="CEO Approval Request Email Summary",
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            # Move to CEO approval state
            rec.write({'state': 'ceo_approval'})

    def action_ceo_approved(self):
        for rec in self:
            # Get outgoing mail server
            server = self.env['ir.mail_server'].sudo().search([], order='sequence asc', limit=1)
            if not server:
                raise ValidationError(_("No outgoing mail server configured."))

            # Get petty cash creator's email (work_email first, fallback to partner email)
            creator_email = None
            creator_emp = self.env['hr.employee'].sudo().search([('user_id', '=', rec.create_uid.id)], limit=1)
            if creator_emp and creator_emp.work_email:
                creator_email = creator_emp.work_email
            elif rec.create_uid.partner_id and rec.create_uid.partner_id.email:
                creator_email = rec.create_uid.partner_id.email

            if not creator_email:
                raise ValidationError(_("No email found for petty cash creator. Please set a work email or user partner email."))

            # Deep link to this record
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            action = self.env.ref('your_module.action_petty_cash_request', raise_if_not_found=False)
            action_part = f"&action={action.id}" if action else ""
            record_url = f"{base_url}/web#id={rec.id}&model=petty.cash.request&view_type=form{action_part}"

            # Email HTML
            body_html = f"""
                <div style="font-family:Arial, sans-serif; font-size:14px; color:#111;">
                    <p>Your petty cash request has been <b>approved</b> by {rec.env.user.name}.</p>
                    <p>You can view the request here:</p>
                    <p>
                        <a href="{record_url}"
                           style="background:#1f6feb;color:#ffffff;padding:10px 16px;border-radius:6px;
                                  text-decoration:none;display:inline-block;font-weight:600;">
                            Open Request in Odoo
                        </a>
                    </p>
                </div>
            """

            subject = f"Petty Cash Request Approved by {rec.env.user.name}"

            # Create one-off template
            tmpl = self.env['mail.template'].sudo().create({
                'name': 'Petty Cash Approved (One-off)',
                'model_id': self.env['ir.model']._get_id('petty.cash.request'),
                'subject': subject,
                'body_html': body_html,
                'email_from': server.smtp_user or self.env.user.email_formatted,
                'mail_server_id': server.id,
            })

            # Send mail
            Mail = self.env['mail.mail'].sudo()
            sent_to, errors = [], []
            try:
                tmpl.with_context(mail_notify_force_send=True).send_mail(
                    rec.id,
                    force_send=True,
                    email_values={'email_to': creator_email, 'auto_delete': False},
                )
            except Exception as e:
                errors.append(f"{creator_email}: {e}")
            else:
                mm = Mail.search([('email_to', 'ilike', creator_email), ('subject', '=', subject)], order='id desc', limit=1)
                if mm and mm.state == 'exception':
                    errors.append(f"{creator_email}: {mm.failure_reason or 'Unknown failure'}")
                elif mm and mm.state in ('sent', 'done'):
                    sent_to.append(creator_email)

            # Log summary in chatter
            summary_lines = [f"Recipient: {creator_email}"]
            if sent_to:
                summary_lines.append("✅ Sent successfully")
            if errors:
                summary_lines.append("❌ Errors:\n- " + "\n- ".join(errors))

            rec.message_post(
                body="<pre>%s</pre>" % ("\n".join(summary_lines)),
                subject="CEO Approval Email Summary",
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            # Update state
            rec.write({'state': 'approved'})

    def action_reject(self):
        if not self.reject_reason:
            raise ValidationError(_("Please mention the reason for the rejection...!"))

        for rec in self:
            # Outgoing mail server
            server = self.env['ir.mail_server'].sudo().search([], order='sequence asc', limit=1)
            if not server:
                raise ValidationError(_("No outgoing mail server configured."))

            # Get creator email (work_email first, fallback to partner email)
            creator_email = None
            creator_emp = self.env['hr.employee'].sudo().search([('user_id', '=', rec.create_uid.id)], limit=1)
            if creator_emp and creator_emp.work_email:
                creator_email = creator_emp.work_email
            elif rec.create_uid.partner_id and rec.create_uid.partner_id.email:
                creator_email = rec.create_uid.partner_id.email

            if not creator_email:
                raise ValidationError(_("There is no email present for the petty cash creator. Please set the employee work email or the user partner email."))

            # Deep link to record
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            action = self.env.ref('your_module.action_petty_cash_request', raise_if_not_found=False)
            action_part = f"&action={action.id}" if action else ""
            record_url = f"{base_url}/web#id={rec.id}&model=petty.cash.request&view_type=form{action_part}"

            # Email HTML
            body_html = f"""
                <div style="font-family:Arial, sans-serif; font-size:14px; color:#111;">
                    <p>Your petty cash request has been <b style="color:#c62828;">rejected</b> by {rec.env.user.name}.</p>
                    <p><b>Reason:</b> {rec.reject_reason}</p>
                    <p>You can view the request here:</p>
                    <p>
                        <a href="{record_url}"
                           style="background:#c62828;color:#ffffff;padding:10px 16px;border-radius:6px;
                                  text-decoration:none;display:inline-block;font-weight:600;">
                            Open Request in Odoo
                        </a>
                    </p>
                </div>
            """

            subject = f"Petty Cash Request Rejected by {rec.env.user.name}"

            # Create one-off template
            tmpl = self.env['mail.template'].sudo().create({
                'name': 'Petty Cash Rejected (One-off)',
                'model_id': self.env['ir.model']._get_id('petty.cash.request'),
                'subject': subject,
                'body_html': body_html,
                'email_from': server.smtp_user or self.env.user.email_formatted,
                'mail_server_id': server.id,
            })

            # Send mail
            Mail = self.env['mail.mail'].sudo()
            sent_to, errors = [], []
            try:
                tmpl.with_context(mail_notify_force_send=True).send_mail(
                    rec.id,
                    force_send=True,
                    email_values={'email_to': creator_email, 'auto_delete': False},
                )
            except Exception as e:
                errors.append(f"{creator_email}: {e}")
            else:
                mm = Mail.search([('email_to', 'ilike', creator_email), ('subject', '=', subject)], order='id desc', limit=1)
                if mm and mm.state == 'exception':
                    errors.append(f"{creator_email}: {mm.failure_reason or 'Unknown failure'}")
                elif mm and mm.state in ('sent', 'done'):
                    sent_to.append(creator_email)

            # Log summary in chatter
            summary_lines = [f"Recipient: {creator_email}"]
            if sent_to:
                summary_lines.append("✅ Sent successfully")
            if errors:
                summary_lines.append("❌ Errors:\n- " + "\n- ".join(errors))

            rec.message_post(
                body="<pre>%s</pre>" % ("\n".join(summary_lines)),
                subject="Rejection Email Summary",
                message_type='comment',
                subtype_xmlid='mail.mt_note',
            )

            # Update state
            rec.write({'state': 'reject'})

class PettyCashLine(models.Model):
    _name = 'petty.cash.line'
    _description = 'Petty Cash Line'

    cash_request_id = fields.Many2one('petty.cash.request', string='Petty Cash Request')
    particulars = fields.Char(string='Particulars')
    supplier_id = fields.Many2one('res.partner', string='Supplier')
    supplier_name = fields.Char(
        string='Supplier',
    )
    reference = fields.Char(string='Reference')
    division = fields.Char(string='Division')
    amount = fields.Float(string='Amount')
    attachment_ids = fields.Many2many("ir.attachment", string="Attachment", tracking=True)
    rejected = fields.Boolean(string="Rejected", readonly=1)
   
    def action_reject_line(self):
        for line in self:
            if not line.rejected:
                line.rejected = True

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        if result.attachment_ids:
            for attachment in result.attachment_ids:
                if not attachment.res_id:
                    attachment.res_id = result.id
        return result

