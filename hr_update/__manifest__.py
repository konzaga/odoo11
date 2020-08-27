##############################################################################
#
# Copyright (c) 2012 Veone - jonathan.arra@gmail.com
# Author: Jean Jonathan ARRA
#
# Fichier du module hr_synthese
# ##############################################################################
{
    "name" : "Mise à jour HR de Odoo",
    "version" : "1.0",
    "author" : "Jean Jonathan ARRA(VEONE)",
    'category': 'Localization',
    "website" : "http://www.veone.net",
    "depends" : ["base", 'hr', 'hr_contract'],
    "description": """
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
            "views/hr_category_employee_view.xml",
            "views/hr_category_salaire_view.xml",
            "views/res_company_view.xml",
            "views/res_partner_view.xml",
            "views/hr_employee_view.xml",
        ],
    "data":[
            "data/abatements_data.xml",
            "data/categories_employee_data.xml",
        ],
    "installable": True
}
