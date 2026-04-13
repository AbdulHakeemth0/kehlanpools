from odoo import fields, models, _


class HrEmployee(models.Model):
    """Inherit the 'hr_employee' module to add 'Documents' super button."""
    _inherit = 'hr.employee'

    document_count_custom = fields.Integer(compute='_compute_document_count_custom',
                                    string='# Documents',
                                    help="Get total count of Document for"
                                         " an Employee")

    def _compute_document_count_custom(self):
        """Function to obtain the total count of documents."""
        for rec in self:
            rec.document_count_custom = self.env['hr.employee.document'].search_count(
                [('employee_id', '=', rec.id)])

    def document_view(self):
        """Function to open the 'hr_employee_document' model."""
        self.ensure_one()
        return {
            'name': _('Documents'),
            'domain': [('employee_id', '=', self.id)],
            'res_model': 'hr.employee.document',
            'type': 'ir.actions.act_window',
            'view_mode': 'list,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                           Click to Create for New Documents
                        </p>'''),
            'limit': 80,
            'context': {'default_employee_id': self.id}
        }
