##############################################################################
#
# Copyright (c) 2012 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_emprunt
# ##############################################################################
{
    "name" : "Emprunt",
    "version" : "1.0",
    "author" : "VEONE",
    "category" : "Generic Modules/Human Resources",
    "website" : "www.veone.net",
    "depends" : ['hr', 'mail', 'hr_payroll'],
    "description": """ Module permettant de gérer les emprunts des employés 
(Echeanciers, Remboursement, interfaçage avec le module de paie)
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "data": [
        'email/notification_email.xml',
    ],
    "update_xml" : [
        "security/groups.xml",
        "security/ir.model.access.csv",
        "views/hr_emprunt_view.xml",
        "views/report_hr_emprunt.xml",
        'report/report.xml',
        "views/hr_demande_emprunt_view.xml",
        "views/hr_advance_salary_view.xml"
       ],
    "installable": True
}
