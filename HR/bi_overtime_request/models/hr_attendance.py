# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._create_or_update_overtime()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._create_or_update_overtime()
        return res

    def _create_or_update_overtime(self):
        for rec in self:
            if not rec.check_in or not rec.check_out:
                continue  # Only process if both check_in and check_out exist

            employee_id = rec.employee_id.id
            first_check_in = rec.check_in
            last_check_out = rec.check_out
            today = rec.check_in.date()

            contract = rec.employee_id.contract_id
            resource_calendar_id = contract.resource_calendar_id if contract and contract.state == 'open' else rec.employee_id.resource_calendar_id

            work_from = 0
            work_to = 0
            lunch_hour = 0
            ot_hours = (last_check_out - first_check_in).total_seconds() / 3600
            weekday = today.weekday()

            if resource_calendar_id and resource_calendar_id.attendance_ids:
                attendance_ids = resource_calendar_id.attendance_ids
                morning = attendance_ids.filtered(lambda x: x.dayofweek == str(weekday) and x.day_period == 'morning')
                if morning:
                    work_from = morning.hour_from
                afternoon = attendance_ids.filtered(lambda x: x.dayofweek == str(weekday) and x.day_period == 'afternoon')
                if afternoon:
                    work_to = afternoon.hour_to
                lunch = attendance_ids.filtered(lambda x: x.dayofweek == str(weekday) and x.day_period == 'lunch')
                if lunch:
                    lunch_hour = lunch.hour_to - lunch.hour_from

            if work_from == 0 and work_to == 0:
                overtime_type = 'holiday_ot'
                overtime_hour = ot_hours
            else:
                standard_work_hours = work_to - work_from - lunch_hour
                without_lunch = ot_hours - lunch_hour
                if without_lunch > standard_work_hours:
                    overtime_type = 'normal_ot'
                    overtime_hour = without_lunch - standard_work_hours
                else:
                    overtime_type = 'normal_ot'
                    overtime_hour = 0

            # Compute pay
            # per_day_wage = contract.wage / 30 if contract else 0
            # hourly_wage = per_day_wage / 8
            amount = overtime_hour * contract.overtime_amount

            # Search and update existing record if exists, else create
            overtime_obj = self.env['bi.overtime'].search([
                ('employee_id', '=', employee_id),
                ('first_check_in', '=', first_check_in),
            ])
            if overtime_obj:
                overtime_obj.write({
                    'last_check_out': last_check_out,
                    'overtime_type': overtime_type,
                    'ot_hours': overtime_hour,
                    'overtime_pay': amount,
                })
            elif overtime_hour > 0:
                self.env['bi.overtime'].create({
                    'employee_id': employee_id,
                    'first_check_in': first_check_in,
                    'last_check_out': last_check_out,
                    'overtime_type': overtime_type,
                    'ot_hours': overtime_hour,
                    'overtime_pay': amount,
                })
