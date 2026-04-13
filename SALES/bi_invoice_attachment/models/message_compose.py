from odoo import models,fields,api,_
import base64
from odoo.exceptions import UserError




class ComposeMessage(models.TransientModel):
    _name = 'whatsapp.compose.message'
    _description = 'whatsapp message'

    sale_id = fields.Many2one(
        'sale.order', 'Sale order', readonly=True)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachment', compute='_compute_attachment_ids', readonly=True, store=True)
    customer_id = fields.Many2one('res.partner',string="Customer", readonly=True)

    def action_send(self):
        if self.customer_id.phone:
            whatsapp_composer = self.env['whatsapp.composer'].with_context({'active_id': self.id}).create(
            {
                'phone': self.customer_id.phone,
                'wa_template_id': self.env.ref(
                    'bi_invoice_attachment.whatsapp_template_invoice_attachment').id,
                'res_model': 'whatsapp.compose.message'
            }
            )
            whatsapp_composer._send_whatsapp_template()
        else:
            raise UserError(_("Please configure customer's phone number."))

    @api.depends('sale_id')
    def _compute_attachment_ids(self):
        sale_order = self.env['sale.order'].browse(self.sale_id.id)
        report = self.env.ref("account.account_invoices_without_payment").sudo()
        pdf_content = self.env['ir.actions.report'].sudo()._render_qweb_pdf(report, [sale_order.id])[0]
        data_record = base64.b64encode(pdf_content)
        if sale_order:
            attachment = self.env['ir.attachment'].create({
                'name': 'Invoice Details',
                'type': 'binary',
                'datas': data_record,
                'res_model': 'whatsapp.compose.message',
                'res_id': self.id,
                'mimetype': 'application/pdf',
            })
            self.attachment_ids = [(6, 0, [attachment.id])]
