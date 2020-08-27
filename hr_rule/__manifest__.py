# -*- coding: utf-8 -*-
{
    'name': "Hr Rules",

    'summary': """
      Ajout du champs société au contrat dans RH""",

    'description': """
        Long description of module's purpose
    """,

    'author': "KERYATEC",
    'website': "http://www.keryatec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_payroll_ci'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}