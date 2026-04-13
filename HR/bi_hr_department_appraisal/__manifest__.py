# -*- coding: utf-8 -*-
{
    'name': 'Employee Department Appraisal',
    'version': '18.0.1.0.3',
    'summary': 'This module helps to add customise functionality in Employee Appraisal.',
    'description': 'This module helps to add customise functionality in Employee Appraisal module.',
    'category': 'HR',
    'author': 'Bassam Infotech LLP',
    'website': 'https://www.bassaminfotech.com',
    'depends': ['base',
                'hr',
                'hr_appraisal'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_department_skill.xml',
        'views/hr_department.xml',
        'views/hr_appraisal.xml',
    ],
    'images': ["bi_hr_department_appraisal/static/description/icon.png"],
    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}

