{
    "name": "Employee Passi Commission",
    "summary": """Employee Commission Calculation""",
    "description": """Employee Commission Calculation""",
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "HRMS",
    "version": "18.0.1.0.3",
    "depends": [
        "base",
        "hr",
        "account",
        "hr_payroll",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/pasi_commission.xml",
        "data/hr_payslip.xml",
        "views/hr_employee.xml"
    ],
}