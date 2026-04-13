# -*- coding: utf-8 -*-
{
    "name": "BI Purchase Order Report",
    "summary": "This module helps to print a Purchase Order pdf report",
    "description": "This module helps to print a Purchase Order pdf",
    "version": "18.0.0.0.3",
    "category": "Purchase",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "depends": ["base","web","purchase"],
    "data": [
        "report/paperformat.xml",
        "report/report_action.xml",
        "report/report_template.xml",
        "report/report_header.xml",
    ],
    'images': [
            '/bi_purchase_order_report/static/src/img/kehlan_pools_logo.png',
            '/bi_purchase_order_report/static/src/img/kehlanpools_fountains_logo.png',

    ],
    "installable": True,
    "license": "LGPL-3",
}
