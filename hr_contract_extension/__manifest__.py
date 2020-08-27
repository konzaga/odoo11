# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_synthese
# ##############################################################################
{
    "name" : "Extension du contrats",
    "version" : "1.0",
    "author" : "VEONE Technologies",
    'category': 'Human Resources',
    "website" : "www.veone.net",
    "depends" : ['base',"hr_contract", 'hr_payroll'],
    "description": """ Extension du contrats de travail des employés
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [

        ],
    "data":[
           "security/ir.model.access.csv",
            "data/primes_data.xml",
           #  "wizard/hr_contract_closed.xml",
           #  "wizard/hr_reverse_contract.xml",
            "wizard/hr_compute_inverse_view.xml",
           #  # "views/res_country_view.xml",
            "views/hr_employee_view.xml",
            "views/hr_convention_view.xml",
            "views/hr_contract_view.xml",
            ],
    "installable": True
}
