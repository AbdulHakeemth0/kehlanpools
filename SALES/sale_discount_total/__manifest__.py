{
    'name': 'Sale Discount on Total Amount',
    'version': '18.0.1.0.1',
    'category': 'Sales Management',
    'summary': "Discount on Total in Sale and Invoice With Discount Limit "
               "and Approval",
    'description': "This module is designed to manage discounts on the total "
                   "amount in sales. It will include features to apply "
                   "discounts either as a specific amount or a percentage. "
                   "This module will enhance the functionality of Odoo's sales "
                   "module, allowing users to easily manage and apply discounts"
                   " to sales orders based on their requirements.",
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'website': "https://bassaminfotech.com",
    'depends': ['sale_management', 'account'],
    'data': [
        'data/analytic_cron.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order_views.xml',
        'views/account_move_views.xml',
        'views/account_move_templates.xml',
        'views/sale_order_templates.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
