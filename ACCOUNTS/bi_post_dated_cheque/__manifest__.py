{
    "name": "Cheque Maintenance",
    "summary": """
        Manage post-dated cheques with automated cheque generation""",
    "description": """
        This module helps in managing post-dated cheques by allowing users to generate cheque lines
        with cheque number, cheque date, cheque amount, and remarks. Users can generate cheque lines
        automatically by providing the starting cheque number and number of cheques.

    """,
    "author": "Bassam Infotech LLP",
    "website": "https://bassaminfotech.com",
    "support": "sales@bassaminfotech.com",
    "license": "OPL-1",
    "category": "Account",
    "version": "18.0.1.0.4",
    "depends": ['base', 'account'],
    "data": [
        'security/ir.model.access.csv',
        'views/post_dated_cheque_views.xml',
    ],
}
