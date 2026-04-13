# -*- coding: utf-8 -*-
{
    'name': 'Annual Leave Allocation',
    'version': '18.0.1.0.3',
    'summary': 'This module helps to add customise functionality in Attendance module.',
    'description': 'This module helps to add customise functionality in Attendance module.',
    'category': 'HR',
    'author': 'Bassam Infotech LLP',
    'website': 'https://www.bassaminfotech.com',
    'depends': ['hr_payroll','base','hr_holidays'],
    'data': [
            'security/ir.model.access.csv',
            'data/employee_salary_rule.xml',
            'views/hr_leave.xml',
            'views/hr_employee.xml',
            'views/hr_leave_type.xml',
            'wizard/leave_salary_wizad.xml',
    ],
    'images': ["bi_leave_allocation/static/description/icon.png"],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
