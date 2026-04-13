# -*- coding: utf-8 -*-
{
    'name': 'Employee Salary Report',
    'version': '18.0.1.0.3',
    'summary': 'This module helps to add customise functionality in employee salary report module.',
    'description': 'This module helps to add customise functionality in employee salary report module.',
    'category': 'HR',
    'author': 'Bassam Infotech LLP',
    'website': 'https://www.bassaminfotech.com',
    'depends': ['base',
                'hr',
                'report_xlsx',
                'hr_contract',
                'bi_employee_generic_customisation'
                ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/wps_report_wizard.xml',
        'report/wps_report.xml',
        # 'views/hr_employee.xml',

    ],
    'images': ["bi_wps_excel_report/static/description/icon.png"],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
