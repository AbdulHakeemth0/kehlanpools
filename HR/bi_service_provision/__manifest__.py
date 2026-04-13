
{
    'name': 'BI Service Provision',
    'summary': ''' BI Service Provision ''',
    'description': '''BI Service Provision''',
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'maintainer': 'Bassam Infotech LLP',
    'website': 'https://bassaminfotech.com',
    'category': 'hr',
    'depends': ['hr', 'account','base','l10n_ae_hr_payroll','hr_payroll'],
    'version': '18.0.1.0.4',
    'data': [
        "security/ir.model.access.csv",
        "data/payroll_rule.xml",
        "views/gratuity_provision.xml",
        "views/hr_payroll.xml",
        "views/hr_employee.xml",
        "views/hr_contract.xml",
        # "data/gratuity_pay_rule.xml",
    ],
    'images': [],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
}

