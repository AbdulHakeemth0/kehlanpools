{
    "name": "Petty Cash New",
    "version": "18.0.0.2.0",
    "category": "Accounting",
    "summary": "Petty Cash New Workflow with PDF Report",
    "description": "Petty cash form with approval workflow and report generation.",
    "depends": ["base", "account", "mail", "bi_petty_cash"],
    "data": [
        "security/ir.model.access.csv",
        "data/petty_cash_new_sequence.xml",
        "views/petty_cash_form_view.xml",
        "views/petty_cash_menu.xml",
        "report/paper_format.xml",
        "report/petty_cash_report.xml",
        "report/header.xml",
        "report/petty_cash_template.xml"
    ],
    "installable": True,
    "application": True,
    "auto_install": False
}
