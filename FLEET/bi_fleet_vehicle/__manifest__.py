{
    'name': 'bi fleet vehicle',
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'maintainer': 'Bassam Infotech LLP',
    'website': 'https://bassaminfotech.com',
    'version': '18.0.1.0.1',
    'category': 'fleet',
    'summary': ''' bi fleet vehicle''',
    'description': '''bi fleet vehicle''',
    'depends': ['fleet','hr','documents_fleet','bi_fleet'],
    'data': [
        "security/ir.model.access.csv",
        "views/fleet_vehicle.xml",
        "views/damage_history.xml"
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'images': [],
    'installable': True,
    'application': False,
    'images': [],
    'license': 'OPL-1',
}
