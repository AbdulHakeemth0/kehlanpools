{
    "name": "PDC",
    "summary": """
        PDC""",
    "description": """
        Long description of module's purpose
    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "category": "Accounting",
    "version": "18.0.1.0.1",
    "license": "OPL-1",
    "depends": ['mail','base', 'account'],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/sequence.xml",
        "data/cron.xml",
        "data/notification_activity.xml",
        "views/post_dated_check.xml",
        "views/account_move.xml",
        # "views/pdc_configuration.xml",
        "views/account_account.xml",
        "views/res_company.xml",
        "views/pdc_server_action.xml",
        "wizards/bi_pdc_wizard_view.xml",
        "reports/paperformat.xml",
        "reports/payment_action.xml",
        "reports/payment_voucher_pdf_report.xml",
    ],
}
