# -*- coding: utf-8 -*-
{
    'name': "Quảnh lý Bảo Hiểm",

    'summary': """
        Quản lý Bảo Hiểm""",

    'description': """
        Đây là module quản lý bảo hiểm của người lao động. Gồm: Bảo Hiểm Xã Hội, Bảo Hiểm Y Tế và Bảo Hiểm Thất Nghiệp
    """,

    'author': "VWS",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/bao_hiem_views.xml',
    ],
}