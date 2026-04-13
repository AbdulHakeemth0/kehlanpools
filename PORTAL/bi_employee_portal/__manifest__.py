# -*- coding: utf-8 -*-
{
    'name': 'Bi Employee Portal',
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'maintainer': 'Bassam Infotech LLP',
    'website': 'https://bassaminfotech.com',
    'version': '18.0.1.0.1',
    'category': 'HR',
    'summary': 'PORTAL FOR EMPLOYEES',
    'description': """ PORTAL FOR EMPLOYEES """,
    'depends': ['base','portal', 'hr', 'hr_holidays','bi_helpdesk_portal'],
    'data': [
        "security/ir.model.access.csv",
        "views/hr_leave_template.xml",
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'images': [],
}

