# -*- coding: utf-8 -*-
{
    'name': 'Overtime Request',
    'version': '18.0.1.0.5',
    'summary': 'This module helps to add customise functionality in Attendance module.',
    'description': 'This module helps to add customise functionality in Attendance module.',
    'category': 'HR',
    'author': 'Bassam Infotech LLP',
    'website': 'https://www.bassaminfotech.com',
    'depends': ['hr_attendance',
                'hr',
                'hr_payroll',
                'hr_contract',
                ],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/bi_overtime.xml',
        'views/hr_contract.xml',

    ],
    'images': ["bi_overtime_request/static/description/icon.png"],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
