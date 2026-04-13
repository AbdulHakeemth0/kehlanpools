{
    'name': 'Invoice Attachment',
    'summary': ''' Invoice Attachment ''',
    'description': '''Invoice Attachment''',
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'maintainer': 'Bassam Infotech LLP',
    'website': 'https://bassaminfotech.com',
    'category': 'stock',
    'depends': ['sale', 'whatsapp','account_reports','sale_subscription'],
    'version': '18.0.0.0.1',
    'data': [
        'security/ir.model.access.csv',
        'views/meassage_compose.xml',
        'data/whatsapp_template_data.xml',
        'views/sale_order.xml',
        
    ],
    'images': [],
    'license': 'OPL-1',
    'installable': True,
    'application': False,
}
