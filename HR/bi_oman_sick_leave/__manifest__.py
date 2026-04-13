{
    'name': 'Oman Sick Leave Payroll',
    'version': '18.0.0.0.0',
    'summary': 'Implements sick leave payment structure as per Oman labor law.',
    'category': 'Payroll',
    'author': 'Bassam Infotech LLP',
    'website': 'https://www.bassaminfotech.com',
    'depends': ['hr', 'hr_payroll','base'],
    'data': [
        'views/hr_leave_type.xml',
        'data/sick_leave_sal_rule.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
