##############################################################################
#
# Copyright (c) 2012 Veone - jonathan.arra@gmail.com
# Author: Jean Jonathan ARRA
#
# Fichier du module hr_synthese
# ##############################################################################
{
    "name" : "Payroll Côte d'Ivoire",
    "version" : "1.0",
    "author" : "Jean Jonathan ARRA",
    'category': 'Localization',
    "website" : "http://www.siig.ci",
    "depends" : ["hr_payroll","hr_contract_extension", 'web'],
    "description": """ Synthèse de la paie
    - livre de paie mensuelle et périodique
    - Synthèse de paie des employés
    - interfaçage avec la gestion des contrats des employés
    """,
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
                    "views/hr_payroll_report.xml",
                    #"security/hr_security.xml",
                    "security/ir.model.access.csv",
                    'report/templates/layout_view.xml',
                    "wizards/hr_payroll_inverse_view.xml",
                    "views/res_company_view.xml",
                    "views/report_payslip.xml",
                    "views/hr_payroll_ci.xml",
                    ],
     "data":[
            'data/hr_salary_rule_category.xml',
            'data/hr_salary_rule.xml',
            # 'data/hr_rule_input.xml',
            # 'data/hr_payroll_structure.xml',
            #'data/hr_structure_salary_rule_rel.xml',
            ],
    "installable": True
}
