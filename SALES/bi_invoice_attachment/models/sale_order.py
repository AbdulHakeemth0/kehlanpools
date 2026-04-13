from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def send_by_whatsapp(self):
       view = self.env.ref('bi_invoice_attachment.message_compose_form_view_id')
       return {
                'name': _('Odoo'),
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'whatsapp.compose.message',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': {
                    'default_sale_id': self.id,
                    'default_customer_id':self.partner_id.id,
                    # 'default_attachment_ids': [(6, 0, invoice_attachment.ids)],
                    },
            }
       
