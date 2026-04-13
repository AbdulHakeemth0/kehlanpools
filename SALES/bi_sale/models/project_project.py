from odoo import fields,models,_,api

class ProjectProject(models.Model):
    _inherit = 'project.project'
    _rec_name = "sequence_no"

    sequence_no = fields.Char('Sequence No.',copy=False, default=lambda self: _('New'))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sequence_no', _("New")) == _("New"):
                vals['sequence_no'] = self.env['ir.sequence'].next_by_code(
                    'project.project') or _("New")
        return super().create(vals_list)