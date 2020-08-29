# -*- coding: utf-8 -*-
{
    'name': "Event Set",

    'summary': """
        Event set""",

    'description': """
        Allows to sell multiple event registrations as a set.
    """,

    'author': "kadogams",
    'website': "https://github.com/kadogams/event_set",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Marketing/Events',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website_sale', 'event_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_views.xml',
        'views/website_sale_templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
