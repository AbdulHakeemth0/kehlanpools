# -*- coding: utf-8 -*-
{
    'name': 'Bi Helpdesk Portal',
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'maintainer': 'Bassam Infotech LLP',
    'website': 'https://bassaminfotech.com',
    'version': '18.0.1.0.2',
    'category': 'PORTAL',
    'summary': 'HELPDESK',
    'description': """ HELPDESK """,
    'depends': ['base','portal','helpdesk','hr','crm_helpdesk','crm','sale'],
    'data': [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/activity.xml",
        "views/bi_helpdesk_portal.xml",
        "views/helpdesk_types.xml",
        "views/hr_employee.xml",
        "views/employee_team.xml",
        "views/help_desk_stage.xml",
        "views/lead.xml",
        "views/sale_order.xml",
        'data/server_action.xml',
        "views/helpdesk_team.xml",
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'images': [],

}
