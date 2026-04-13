from odoo import api, fields, models
from datetime import datetime
from lxml import etree



class Accountinvoice(models.Model):
    _inherit = 'account.move'

    def _compute_amount_in_word(self):
        for rec in self:
            number = '%.2f' % abs(rec.amount_total)
            units_name = rec.currency_id.name
            list = str(number).split('.')
            cents_number = int(list[1])
            if units_name == 'AED':
                cents_name = (cents_number > 1) and '  Only' or '  Only'
            if units_name == 'INR':
                cents_name = (cents_number > 1) and '  Only' or '  Only'
            if units_name == 'USD':
                cents_name = (cents_number > 1) and '  Only' or '  Only'
            rec.num_word = str(rec.currency_id.amount_to_text(rec.amount_total)) + cents_name

    num_word = fields.Char(string="Amount In Words:", compute='_compute_amount_in_word')
    # ts_no = fields.Char(string='TS No')
    # ts_date = fields.Date(string='TS Date')
    lpo_no = fields.Char(string='LPO No')
    # project_id = fields.Many2one('project.project', string='Project')
    quotation_no = fields.Char(string='Quotation No')
    contact_ids = fields.Many2many(
        'res.partner', string='Contact')
    partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        string='Partner', change_default=True)
    proforma_no = fields.Char(string='Proforma No',readonly=True, copy=False)
    project_no = fields.Char(string='Project No')
    job_no = fields.Char(string='Job NO')
    ensure = fields.Text(string='Notes',default="Timesheet Summary ")
    prepared_by_user_id = fields.Many2one('res.users', string='Prepared By:')
    approved_by_user_id = fields.Many2one('res.users', string='Approved By:')
    signature = fields.Image('Signature', help='Signature received through the portal.', copy=False, attachment=True, max_width=1024, max_height=1024)
    signed_by = fields.Char('Signed By', help='Name of the person that signed', copy=False)
    signed_on = fields.Datetime('Signed On', help='Date of the signature.', copy=False)
    delivery_status = fields.Selection([
        ('dispatched', 'Dispatched'),('delivered', 'Delivered')
    ], string='Delivery Status')
    delivery_person_id = fields.Many2one('hr.employee', string='Delivery Person')
    asset_sale = fields.Boolean(string = "Asset Sale",default = False)

    @api.onchange('partner_id')
    def onchange_partnerid(self):
        if self.partner_id:
            child_ids = self.partner_id.child_ids.ids
            domain = {'contact_ids': [('id', 'in', child_ids)]}
            result = {'domain': domain}
            return result

    @api.model_create_multi
    def create(self, vals_list):
        # self.prepared_by_user_id = self.env.user.id
        if vals_list:
            if vals_list[0].get('type', False) == 'out_invoice':
                if not vals_list[0].get('proforma_no', False):
                    if 'company_id' in vals_list:
                        vals_list[0]['proforma_no'] = self.env['ir.sequence'].with_context(force_company=vals_list[0]['company_id']).next_by_code('proforma.invoice.no')
                    else:
                        vals_list[0]['proforma_no'] = self.env['ir.sequence'].next_by_code('proforma.invoice.no')
                    vals_list[0]['prepared_by_user_id'] = self.env.user.id
            return super(Accountinvoice, self).create(vals_list)

    def action_post(self):
        result = super(Accountinvoice, self).action_post()
        for order in self:
            order.approved_by_user_id = self.env.user.id
        return result

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Overrides orm field_view_get.
        @return: Dictionary of Fields, arch and toolbar.
        """

        res = super(Accountinvoice, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        doc = etree.XML(res['arch'])
        nodes = doc.xpath("//field[@name='contact_ids']")
        if self._context.get('default_partner_id', False):
            child_ids = self.env['res.partner'].browse(self._context.get('default_partner_id', False)).child_ids.ids
            for node in nodes:
                node.set('domain', "[('id', 'in',["+','.join(map(str, child_ids)) +"])]")
            res['arch'] = etree.tostring(doc)
        return res

    # def _reverse_moves(self, default_values_list=None, cancel=False):
    #     ''' Reverse a recordset of account.move.
    #     If cancel parameter is true, the reconcilable or liquidity lines
    #     of each original move will be reconciled with its reverse's.

    #     :param default_values_list: A list of default values to consider per move.
    #                                 ('type' & 'reversed_entry_id' are computed in the method).
    #     :return:                    An account.move recordset, reverse of the current self.
    #     '''
    #     if not default_values_list:
    #         default_values_list = [{} for move in self]

    #     if cancel:
    #         lines = self.mapped('line_ids')
    #         # Avoid maximum recursion depth.
    #         if lines:
    #             lines.remove_move_reconcile()

    #     reverse_type_map = {
    #         'entry': 'entry',
    #         'out_invoice': 'out_refund',
    #         'out_refund': 'entry',
    #         'in_invoice': 'in_refund',
    #         'in_refund': 'entry',
    #         'out_receipt': 'entry',
    #         'in_receipt': 'entry',
    #     }

    #     move_vals_list = []
    #     for move, default_values in zip(self, default_values_list):
    #         default_values.update({
    #             'type': reverse_type_map[move.type],
    #             'reversed_entry_id': move.id,
    #         })
    #         move_vals_list.append(move.with_context(move_reverse_cancel=cancel)._reverse_move_vals(default_values, cancel=cancel))
    #     if move_vals_list:
    #         reverse_moves = self.env['account.move'].create(move_vals_list)
    #     else:
    #         reverse_moves = self.env['account.move']
    #     for move, reverse_move in zip(self, reverse_moves.with_context(check_move_validity=False)):
    #         # Update amount_currency if the date has changed.
    #         if move.date != reverse_move.date:
    #             for line in reverse_move.line_ids:
    #                 if line.currency_id:
    #                     line._onchange_currency()
    #         reverse_move._recompute_dynamic_lines(recompute_all_taxes=False)
    #     reverse_moves._check_balanced()

    #     # Reconcile moves together to cancel the previous one.
    #     if cancel:
    #         reverse_moves.with_context(move_reverse_cancel=cancel).post()
    #         for move, reverse_move in zip(self, reverse_moves):
    #             accounts = move.mapped('line_ids.account_id') \
    #                 .filtered(lambda account: account.reconcile or account.internal_type == 'liquidity')
    #             for account in accounts:
    #                 (move.line_ids + reverse_move.line_ids)\
    #                     .filtered(lambda line: line.account_id == account and line.balance)\
    #                     .reconcile()
    #             reverse_moves.write({"lpo_no":move.name})
    #     return reverse_moves


class AccountMove(models.Model):
    _inherit = 'account.move.line'

    ts_no = fields.Char(string='TS No')
    ts_date = fields.Date(string='TS Date')
    tax_amount = fields.Monetary(string="Tax Amount",
        compute="compute_tax_amount")
    lpo_no = fields.Char(string='LPO No')
    # task_id = fields.Many2one('project.task', string="Task")

    @api.depends('tax_ids')
    def compute_tax_amount(self):
        for order in self:
            order.tax_amount = order.price_total - order.price_subtotal


    def change_tag(self):
        records = self.env["account.move.line"].search([("tag_ids","in",[29]),("account_id",'=',45),("journal_id","=",13)])
        for order in records:
            order.tag_ids = [(6,0,[57])]

class res_partner(models.Model):
    _inherit = 'res.partner'

    rating = fields.Char('Rating')

# class ProjectTask(models.Model):
#     _inherit = 'project.task'
#
#     def name_get(self):
#         result = []
#         for line in self:
#             if line.sequence_code:
#                 result.append((line.id,'[' + line.sequence_code + ']' + (line.name or '') ))
#             else:
#                 result.append((line.id, line.name))
#         return result
