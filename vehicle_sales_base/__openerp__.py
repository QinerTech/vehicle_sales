# -*- coding: utf-8 -*-
{
    'name': "汽车销售基础",

    'summary': """
        本模块定义了汽车销售解决方案的基础数据

        """,

    'description': """
        本模块定义了汽车销售解决方案的基础数据
        1，角色
        2，权限
        3，菜单系统



    """,

    'author': "Your Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['crm', 'sale', 'purchase', 'account_voucher', 'account_accountant', 'stock'],

    # always loaded
    'data': [
        'data.xml',
        'templates.xml',
        'security/roles.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
