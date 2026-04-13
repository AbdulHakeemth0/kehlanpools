# -*- coding: utf-8 -*-
{
    "name": "BI Tax Invoice Report",
    "summary": "This module helps to print a tax invoice pdf report",
    "description": "This module helps to print a tax invoice pdf report",
    "version": "18.0.1.9.10",
    "category": "ACCOUNT",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "depends": ["account","base","web","sale","sale_subscription","bi_vas_amc"],
    "data": [
        "report/paperformat.xml",
        "report/report_action.xml",
        "report/report_template.xml",
        "views/res_bank.xml",
        "views/sale_order.xml",
        "views/account_move_line.xml",
        "report/report_header.xml"
    ],
    'images': [
            '/bi_amc_tax_invoice/static/src/img/kehlan_pools_logo.png',
            '/bi_amc_tax_invoice/static/src/img/kehlanpools_fountains_logo.png',

    ],
    "installable": True,
    "license": "LGPL-3",
}
