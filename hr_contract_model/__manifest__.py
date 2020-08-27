# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2015 Veone - support.veone.net
# Author: Veone Technologies
#
# Fichier du module hr_contract_model
# ##############################################################################
{
    "name" : "Contracts Models",
    "version" : "1.0",
    "author" : "VEONE Technologies",
    'category': 'Human Resources',
    "website" : "www.veone.net",
    "depends" : ["hr_contract","hr_payroll"],
    "description": """ 
        estion des modèles de contracts
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
            "security/ir.model.access.csv",
            "views/hr_contract_model_view.xml",
        ],
    "data":[
           
            ],
    "installable": True
}
