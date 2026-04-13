{
    "name": "Petty Cash",
    "summary": """
        Module is used to do petty cash customisation""",
    "description": """
        Module is used to do petty cash customisation
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Account",
    "version": "18.0.1.0.3",
    "depends": ["account", "hr","account_payment","accountant","base","bi_vas_amc"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/activity.xml",
        "data/ir_sequence_data.xml",
        "views/account_journal.xml",
        "views/petty_cash_expenses.xml",
        "views/petty_cash_imbursement.xml",
        "views/petty_transfer.xml",
    ],
}
