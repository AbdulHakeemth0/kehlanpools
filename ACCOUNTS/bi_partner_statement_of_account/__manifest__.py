{
    "name": "Customer/Vendor Account Statement",
    "version": "18.0.0.2",
    "category": "Account",
    "license": "OPL-1",
    "depends": [
        "account",
        "account_accountant",
        "account_followup",
        "report_xlsx",
    ],
    "description": """
        This Module Is For Customer/Vendor Account Statement.
    """,
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "report/ageing_bucket.xml",
        "report/report_template.xml",
        "report/account_followup_report_new.xml",
        "wizard/account_statement_wizard_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
