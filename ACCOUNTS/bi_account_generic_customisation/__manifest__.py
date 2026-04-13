{
    "name": "Account Generic Customisation",
    "summary": """Customizations to the account module, adding enhanced features for accounting workflows.""",
    "description": """ 
        This module introduces several customizations and enhancements to the accounting module in Odoo, 
        including improvements to invoice management, reports, and warranty tracking related to products.
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Account",
    "version": "18.0.1.0.7",
    "depends": ["account", "accountant","base","account_accountant"],
    "data": [
        "data/data.xml",
        "security/security.xml",
        "views/account_move.xml",
        "views/account_payment.xml",
        "views/account_journal.xml",
    ],
}
