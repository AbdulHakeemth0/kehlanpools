# -*- coding: utf-8 -*-
{
    'name': 'Bi Payment Portal',
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'maintainer': 'Bassam Infotech LLP',
    'website': 'https://bassaminfotech.com',
    'version': '18.0.1.0.1',
    'category': 'ACCOUNTS',
    'summary': 'CUSTOMER PAYMENT',
    'description': """ CUSTOMER PAYMENT """,
    'depends': ['base','portal','account'],
    'data': [
        "security/ir.model.access.csv",
        "views/payment_portal_views.xml",
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'images': [],

}
