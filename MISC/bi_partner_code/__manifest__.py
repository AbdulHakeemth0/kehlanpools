{
    'name': 'Partner Code Automatic Generation in Odoo 18',
    'summary': 'Auto-generate and display partner codes',
    'version': '18.0.0.0.1',
    'category': 'Contacts',
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'maintainer': 'Bassam Infotech LLP',
    'website': 'https://bassaminfotech.com',
    'depends': ['base','bi_customer_code'],
    'data': [
        'data/partner_sequence.xml',
        'data/server_action.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}