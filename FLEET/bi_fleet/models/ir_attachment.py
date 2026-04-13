from odoo import fields, models

class IrAttachment(models.Model):
    """Inherit the 'ir_attachment' model to retrieve attached documents."""
    _inherit = 'ir.attachment'

    # doc_attach_ids = fields.Many2many('vehicle.document',
    #                                   'doc_attachment_ids',
    #                                   'attach_id2',
    #                                   'doc_id',
    #                                   string="Attachment", invisible=1,
    #                                   help="Choose Employee Document for"
    #                                        " Attachment")
    doc_attach_ids = fields.Many2many('vehicle.document',
                                        string="Attachment",
                                        invisible=1,
                                        help="Choose Vehicle Document for Attachment"
)

    def _valid_field_parameter(self, field, name):
        return name in ['invisible'] or super()._valid_field_parameter(field, name)
