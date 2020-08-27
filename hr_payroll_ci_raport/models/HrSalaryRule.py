# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2015 - SIIGCI - jonathan.arra@gmail.com
# Author: Jean Jonathan ARRA
#
# Fichier du module hr_payroll_ci_raport
# ##############################################################################



from odoo import fields, models

class HrPayslipSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _order = 'sequence'

    appears_on_payroll = fields.Boolean(string='Apparaît sur le Livre de paie', default=False,
        help="Utilisé pour afficher la règle salariale sur le livre de paie")
