from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class AccountFollowupReportXlsx(models.AbstractModel):
    _name = "report.bi_partner_statement_of_account.os_statement_xlsx"
    _description = "Statement of account Excel Report"
    _inherit = ["report.report_xlsx.abstract", "report.bi_partner_statement_of_account.outstanding_statement"]

    def generate_xlsx_report(self, workbook, data, objects):
        worksheet = workbook.add_worksheet("Report")
        format1 = workbook.add_format(
            {
                "font_size": 14,
                "bottom": True,
                "right": True,
                "left": True,
                "top": True,
                "align": "center",
                "bold": True,
            }
        )

        format3 = workbook.add_format({"bottom": True, "top": True, "font_size": 12})
        number_format_alignc = workbook.add_format({"align": "center", "num_format": "#,##0.00"})
        number_format_boldl = workbook.add_format({"align": "left", "num_format": "#,##0.00", "bold": True})
        number_format_boldc = workbook.add_format({"align": "center", "num_format": "#,##0.00", "bold": True})
        number_format = workbook.add_format({"num_format": "#,##0.00"})
        font_size_8 = workbook.add_format({"bottom": True, "top": True, "right": True, "left": True, "font_size": 8})
        justify = workbook.add_format({"bottom": True, "top": True, "right": True, "left": True, "font_size": 12})
        format3.set_align("center")
        font_size_8.set_align("center")
        justify.set_align("justify")
        format1.set_align("center")
        boldc = workbook.add_format({"bold": True, "align": "center"})
        boldl = workbook.add_format({"bold": True, "align": "left"})
        boldr = workbook.add_format({"bold": True, "align": "right"})
        alignc = workbook.add_format({"align": "center"})
        heading_format = workbook.add_format(
            {
                "bold": True,
                "align": "center",
                "font_color": "black",
                "bg_color": "#999999",
            }
        )

        worksheet.set_column("A:A", 25)
        worksheet.set_column("B:B", 20)
        worksheet.set_column("C:C", 20)
        worksheet.set_column("D:D", 20)
        worksheet.set_column("E:E", 20)
        worksheet.set_column("F:F", 20)
        worksheet.set_column("G:G", 20)
        worksheet.set_column("H:H", 20)
        worksheet.set_column("I:I", 20)

        company_id = data["company_id"]
        partner_ids = data["partner_ids"]
        date_start = data.get("date_start")
        if date_start and isinstance(date_start, str):
            date_start = datetime.strptime(
                date_start, DEFAULT_SERVER_DATE_FORMAT
            ).date()
        date_end = data["date_end"]
        if isinstance(date_end, str):
            date_end = datetime.strptime(date_end, DEFAULT_SERVER_DATE_FORMAT).date()
        account_type = data["account_type"]
        aging_type = data["aging_type"]
        today = fields.Date.today()
        amount_field = data.get("amount_field", "open_amount")

        # There should be relatively few of these, so to speed performance
        # we cache them - default needed if partner lang not set
        self._cr.execute(
            """
            SELECT p.id, l.date_format
            FROM res_partner p LEFT JOIN res_lang l ON p.lang=l.code
            WHERE p.id IN %(partner_ids)s
            """,
            {"partner_ids": tuple(partner_ids)},
        )
        date_formats = {r[0]: r[1] for r in self._cr.fetchall()}
        default_fmt = self.env["res.lang"]._lang_get(self.env.user.lang).date_format
        currencies = {x.id: x for x in self.env["res.currency"].search([])}

        res = {}
        # get base data
        lines = self._get_account_display_lines(
            company_id, partner_ids, date_start, date_end, account_type
        )
        balances_forward = self._get_account_initial_balance(
            company_id, partner_ids, date_start, account_type
        )

        if data["show_aging_buckets"]:
            buckets = self._get_account_show_buckets(
                company_id, partner_ids, date_end, account_type, aging_type
            )
            bucket_labels = self._get_bucket_labels(date_end, aging_type)
        else:
            bucket_labels = {}

        # organise and format for report
        format_date = self._format_date_to_partner_lang
        partners_to_remove = set()
        for partner_id in partner_ids:
            res[partner_id] = {
                "today": format_date(today, date_formats.get(partner_id, default_fmt)),
                "start": format_date(
                    date_start, date_formats.get(partner_id, default_fmt)
                ),
                "end": format_date(date_end, date_formats.get(partner_id, default_fmt)),
                "currencies": {},
            }
            currency_dict = res[partner_id]["currencies"]

            for line in balances_forward.get(partner_id, []):
                (
                    currency_dict[line["currency_id"]],
                    currencies,
                ) = self._get_line_currency_defaults(
                    # line["currency_id"], currencies, line["balance"]
                    line["currency_id"], currencies, line["balance"], currency_dict[line["currency_id"]]["amount_due"]
                )

            for line in lines[partner_id]:
                if line["currency_id"] not in currency_dict:
                    (
                        currency_dict[line["currency_id"]],
                        currencies,
                    ) = self._get_line_currency_defaults(
                        line["currency_id"], currencies, 0.0, 0.0
                    )
                line_currency = currency_dict[line["currency_id"]]
                if not line["blocked"]:
                    line_currency["amount_due"] += line[amount_field]
                line["balance"] = line_currency["amount_due"]
                line["date"] = format_date(
                    line["date"], date_formats.get(partner_id, default_fmt)
                )
                line["date_maturity"] = format_date(
                    line["date_maturity"], date_formats.get(partner_id, default_fmt)
                )
                line_currency["lines"].append(line)

            if data["show_aging_buckets"]:
                for line in buckets[partner_id]:
                    if line["currency_id"] not in currency_dict:
                        (
                            currency_dict[line["currency_id"]],
                            currencies,
                        ) = self._get_line_currency_defaults(
                            line["currency_id"], currencies, 0.0, 0.0
                        )
                    line_currency = currency_dict[line["currency_id"]]
                    line_currency["buckets"] = line

            if len(partner_ids) > 1:
                values = currency_dict.values()
                if not any([v["lines"] or v["balance_forward"] for v in values]):
                    if data["filter_non_due_partners"]:
                        partners_to_remove.add(partner_id)
                        continue
                    else:
                        res[partner_id]["no_entries"] = True
                if data["filter_negative_balances"]:
                    if not all([v["amount_due"] >= 0.0 for v in values]):
                        partners_to_remove.add(partner_id)

        for partner in partners_to_remove:
            del res[partner]
            partner_ids.remove(partner)
        
        row_new = 9

        for each_partner in res:
            partner_id = self.env["res.partner"].browse(each_partner)
            worksheet.merge_range("A1:G2", "Statement of Account", heading_format)
            worksheet.merge_range("A4:G4", "Customer: %s " % partner_id.name if partner_id else "", boldc)
            worksheet.merge_range(
                "A5:G5",
                "Address: %s%s%s%s "
                % (
                    f"{partner_id.street}," if partner_id.street else "",
                    f"{partner_id.street2}," if partner_id.street2 else "",
                    f"{partner_id.state_id.name}," if partner_id.state_id.name else "",
                    f"{partner_id.country_id.name}" if partner_id.country_id.name else "",
                ),
                boldc,
            )
            worksheet.merge_range("A6:G6", "Mobile: %s " % partner_id.phone if partner_id.phone else "", boldc)
            worksheet.merge_range("A7:G7", "Date: %s " % res[each_partner]["end"], boldc)
            worksheet.merge_range("E8:G8", "Payment Terms: %s " % partner_id.property_payment_term_id.name, boldc)
            for each in res[each_partner]["currencies"]:
                currency_id = self.env["res.currency"].browse(each)
                if res[each_partner]["currencies"][each]["lines"]:
                    worksheet.merge_range("A{}:G{}".format(row_new, row_new), "Currency: %s " % currency_id.name, boldl)
                    
                    row_new += 1
                    total_due_amount = "{:,.2f}".format(res[each_partner]["currencies"][each]['amount_due'])
                    worksheet.merge_range(
                        "A{}:C{}".format(row_new, row_new),
                        "TOTAL DUE AMOUNT: {} {}".format(total_due_amount, currency_id.name),
                        number_format_boldl,
                    )
                    amount_over_due = 0
                    if res[each_partner]["currencies"][each]['buckets']:
                        buckets = res[each_partner]["currencies"][each]['buckets']
                        amount_over_due += buckets.get('b_1_30', 0.0) + buckets.get('b_30_60', 0.0) + buckets.get('b_60_90', 0.0) + buckets.get('b_90_120', 0.0) + buckets.get('b_over_120', 0.0)

                    total_overdue = "{:,.2f}".format(amount_over_due)
                    worksheet.merge_range(
                        "D{}:G{}".format(row_new, row_new),
                        "TOTAL OVERDUE: {} {}".format(total_overdue, currency_id.name),
                        number_format_boldl,
                    )

                    row_new += 2
                    worksheet.write("A%s" % row_new, "Current", heading_format)
                    worksheet.write("B%s" % row_new, "0-30 Days", heading_format)
                    worksheet.write("C%s" % row_new, "31-60 Days", heading_format)
                    worksheet.write("D%s" % row_new, "61-90 Days", heading_format)
                    worksheet.write("E%s" % row_new, "91-120 Days", heading_format)
                    worksheet.write("F%s" % row_new, "120+ Days", heading_format)
                    worksheet.write("G%s" % row_new, "", heading_format)
                    
                    row_new += 1
                    worksheet.write("A%s" % row_new, buckets.get('current', 0.0), number_format_alignc)
                    worksheet.write("B%s" % row_new, buckets.get('b_1_30', 0.0), number_format_alignc)
                    worksheet.write("C%s" % row_new, buckets.get('b_30_60', 0.0), number_format_alignc)
                    worksheet.write("D%s" % row_new, buckets.get('b_60_90', 0.0), number_format_alignc)
                    worksheet.write("E%s" % row_new, buckets.get('b_90_120', 0.0), number_format_alignc)
                    worksheet.write("F%s" % row_new, buckets.get('b_over_120', 0.0), number_format_alignc)

                    row_new += 2
                    worksheet.write("A%s" % row_new, "Inv No", heading_format)
                    worksheet.write("B%s" % row_new, "Inv Date", heading_format)
                    worksheet.write("C%s" % row_new, "Due Date", heading_format)
                    worksheet.write("D%s" % row_new, "LPO", heading_format)
                    worksheet.write("E%s" % row_new, "Inv.Amt", heading_format)
                    worksheet.write("F%s" % row_new, "Bal.Amt", heading_format)
                    worksheet.write("G%s" % row_new, "Cum.Bal", heading_format)

                    row_new += 1

                    for each_inv in res[each_partner]["currencies"][each]["lines"]:
                        worksheet.write("A%s" % row_new, each_inv["move_id"], number_format)
                        worksheet.write("B%s" % row_new, each_inv["date"])
                        worksheet.write("C%s" % row_new, each_inv["date_maturity"])
                        worksheet.write("D%s" % row_new, each_inv["lpo_no"])
                        worksheet.write("E%s" % row_new, each_inv["amount"] if "amount" in each_inv else 0, number_format)
                        worksheet.write("F%s" % row_new, each_inv["open_amount"], number_format)
                        worksheet.write("G%s" % row_new, each_inv["balance"], number_format)
                        row_new += 1

                    worksheet.merge_range("A{}:F{}".format(row_new, row_new), "Sub Total", boldr)
                    worksheet.write("G%s" % row_new, total_due_amount, number_format)
                    row_new += 2
                    worksheet.merge_range(
                        "A{}:G{}".format(row_new, row_new),
                        "Total Outstanding Amount: {} {} ".format(total_due_amount, currency_id.name),
                        boldc,
                    )
                    row_new += 2
