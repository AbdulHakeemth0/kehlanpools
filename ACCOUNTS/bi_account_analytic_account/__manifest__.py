{
    "name": "Analytic Account Customisations",
    "summary": """Customizations to the account module.""",
    "description": """ 
       Analytic account customisations
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Account",
    "version": "18.0.2.3.0",
    "depends": ["account", "accountant","base","sale"],
    "data": [
        'data/server_action.xml',
        "data/ir_sequence.xml",
        "data/scheduled_action.xml",
        "views/analytic_account.xml",
        "views/account_move.xml",
        "views/account_journal.xml",
        "views/purchase_order.xml"

    ],
}
