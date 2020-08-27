# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2012 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_emprunt
# ##############################################################################  -->

from odoo import fields, models, api, _


Type_employee = [('h', 'Horaire'), ('j', 'Journalier'), ('m', 'Mensuel')]

class HrEmployee(models.Model):
    _inherit= 'hr.employee'

    category_id= fields.Many2one('hr.contract.category', 'Catégorie', required=False)
    type= fields.Selection(Type_employee, 'Type', required=False, default=False)