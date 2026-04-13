# -*- coding: utf-8 -*-
{
    "name": "Bi Payment Voucher Printout",
    "version": "18.0.1.0.0",
    "category": "accounting",
    "summary": "Cash  Payment Voucher printout",
    "description": "Module is used to cash Payment Voucher printout",
    "author": 'Bassam Infotech LLP',
    "maintainer": "",
    "website": 'https://bassaminfotech.com',
    "depends": ["base","account"],
    "data": [
            "report/report.xml",
            "report/payment_voucher_header.xml",
            "report/payment_voucher_report.xml",
            'views/account_move.xml'
            ],
    "assets": {},
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
    "application": True
}