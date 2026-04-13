# -*- coding: utf-8 -*-
{
    'name': 'Bi Attendance Portal',
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'maintainer': 'Bassam Infotech LLP',
    'website': 'https://bassaminfotech.com',
    'version': '18.0.2.1.2',
    'category': 'HR',
    'summary': 'PORTAL FOR EMPLOYEES',
    'description': """ PORTAL FOR EMPLOYEES """,
    'depends': ['base','portal', 'hr','hr_attendance'],
    'data': [
        "security/ir.model.access.csv",
        "views/employee_attendance.xml",
        "views/employee_views.xml",
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'images': [],

}
