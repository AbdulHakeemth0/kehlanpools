from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'

    customer_code = fields.Char(string='Customer Code', readonly=True, copy=False)
    vendor_code = fields.Char(string='Vendor Code', readonly=True, copy=False)
    is_customer = fields.Boolean(string="Is Customer")
    is_vendor = fields.Boolean(string="Is Vendor")

    @api.model
    def create(self, vals):
        # Ensure only one of the two flags is True
        if vals.get('is_customer'):
            vals['is_vendor'] = False
            if not vals.get('customer_code'):
                vals['customer_code'] = self.env['ir.sequence'].next_by_code('res.partner.customer_code')

        elif vals.get('is_vendor'):
            vals['is_customer'] = False
            if not vals.get('vendor_code'):
                vals['vendor_code'] = self.env['ir.sequence'].next_by_code('res.partner.vendor_code')

        return super(ResPartner, self).create(vals)

    def write(self, vals):
        for partner in self:
            updated_vals = vals.copy()

            # Handle is_customer toggle
            if 'is_customer' in vals and vals['is_customer']:
                updated_vals['is_vendor'] = False
                if not partner.customer_code:
                    updated_vals['customer_code'] = self.env['ir.sequence'].next_by_code('res.partner.customer_code')
                    partner.vendor_code = False

            # Handle is_vendor toggle
            elif 'is_vendor' in vals and vals['is_vendor']:
                updated_vals['is_customer'] = False
                if not partner.vendor_code:
                    updated_vals['vendor_code'] = self.env['ir.sequence'].next_by_code('res.partner.vendor_code')
                    partner.customer_code = False

            super(ResPartner, partner).write(updated_vals)
        return True


    def action_assign_missing_partner_codes(self):
        for partner in self:
            if partner.customer_rank and not partner.customer_code:
                partner.customer_code = self.env['ir.sequence'].next_by_code('res.partner.customer_code')
            if partner.supplier_rank and not partner.vendor_code:
                partner.vendor_code = self.env['ir.sequence'].next_by_code('res.partner.vendor_code')

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args = args or []
        domain = args[:]
        if name:
            domain = ['|', '|', '|',
                    ('customer_code', operator, name),
                    ('vendor_code', operator, name),
                    ('code', operator, name),
                    ('name', operator, name)] + domain
        partners = self.search(domain, limit=limit)
        return partners.name_get()
    
    def name_get(self):
        result = []
        for rec in self:
            parts = []

            # Always show 'code' if present
            if rec.code:
                parts.append(rec.code)

            # Show customer_code or vendor_code if present
            if rec.customer_code:
                parts.append(rec.customer_code)
            if rec.vendor_code:
                parts.append(rec.vendor_code)

            # Always show name
            parts.append(rec.name)

            # Combine all parts with ' - '
            name = " - ".join(parts)
            result.append((rec.id, name))
        return result



