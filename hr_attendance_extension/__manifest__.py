# -*- coding:utf-8 -*-
##############################################################################
#
# Copyright (c) 2012 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_attendance_extension
# ##############################################################################
{
    "name" : "Extension du module hr_attendance",
    "version" : "1.0",
    "author" : "VEONE Technologies",
    'category': 'Human Resources',
    "website" : "www.veone.net",
    "depends" : ['base',"hr_attendance", "hr_payroll_ci"],
    "description": """ Extension du module de gestion des présences.
    
    """,
    "init_xml" : [],

    "data" : [
        "security/ir.model.access.csv",
        "data/hr_overtimes_data.xml",
        "views/heures_supplementaires_view.xml",
        #"views/wkl_heur_supp.xml",
        #"views/config_view.xml",
    ],
    "demo_xml":[],
    "installable": True
}
