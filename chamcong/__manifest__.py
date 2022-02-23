# -*- coding: utf-8 -*-
{
    'name': "Chấm Công",

    'summary': """
        Chấm công nhân viên theo ca làm việc""",

    'description': """
        Đây là module chấm công theo ca làm việc cho nhân viên VWS
    """,

    'author': "VWS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['planning'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/timekeeping_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
