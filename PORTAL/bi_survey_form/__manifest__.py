# -*- coding: utf-8 -*-
{
    'name': 'Bi CRM Survey Form',
    'author': 'Bassam Infotech LLP',
    'company': 'Bassam Infotech LLP',
    'maintainer': 'Bassam Infotech LLP',
    'website': 'https://bassaminfotech.com',
    'version': '18.0.0.0.0',
    'category': 'PORTAL',
    'summary': 'CRM',
    'description': """ CRM """,
    'depends': ['base','portal','crm','account',],
    'data': [
        "security/ir.model.access.csv",
        "views/bi_survey_form.xml",
        "views/bi_mep_equipments_view.xml",
        "views/bi_customer_views.xml",
    ],

    'demo': [],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
    'images': [],

}
