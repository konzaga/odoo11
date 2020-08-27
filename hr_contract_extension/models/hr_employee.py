# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2012 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_emprunt
# ##############################################################################  -->
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datetime import date

from odoo import fields, osv, models, api
from odoo.tools.translate import _
from odoo import netsvc



class hr_employee_degree(models.Model):
    _name = "hr.employee.degree"
    _description = "Degree of employee"

    name= fields.Char('Name', required=True, translate=True)
    sequence= fields.Integer('Sequence', help="Gives the sequence order when displaying a list of degrees.", default=1)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name of the Degree of employee must be unique!')
    ]


class licence(models.Model):
    _name = "hr.licence"
    _description = "Licence employé"
    
    name= fields.Char('Libellé Licence', size=64, required=True, readonly=False)
    reference= fields.Char('Reférence', size=64, required=False, readonly=False)
    date_debut= fields.Date('Début validité')
    date_fin= fields.Date('Fin validité')
    employee_id= fields.Many2one('hr.employee', 'Employé', required=False)

class domaine(models.Model):
    _name = "hr.diplomes.domaine"
    _description = "Domaine de diplome employe"
    _rec_name = 'libelle'

    libelle= fields.Char('Libellé Domaine', size=64, required=True, readonly=False)

class diplome_employe(models.Model):
    _name = "hr.diplomes.employee"
    _description = "Diplome employe"

    name= fields.Char('Name', size=64, required=False, readonly=False,translate=True)
    diplome_id= fields.Many2one('hr.employee.degree', 'Niveau', required=True)
    domaine_id= fields.Many2one('hr.diplomes.domaine', 'Domaines',required=False, readonly=False)
    reference= fields.Char('Reférence', size=64, required=False, readonly=False)
    date_obtention= fields.Date("Date d'obtention")
    date_start= fields.Date("Date début")
    date_end= fields.Date("Date fin")
    type= fields.Selection([('diplome','Diplôme'),('certif','Certification')],"Type",select=True)
    image= fields.Binary('Image')
    employee_id= fields.Many2one('hr.employee', 'Employé', required=False)

class visa(models.Model):
    _name = "hr.visa"
    _description = "visa employé"

    name= fields.Char('Libellé visa', size=64, required=True, readonly=False)
    reference= fields.Char('N° Visa', size=64, required=True, readonly=False)
    pays_id= fields.Many2one('res.country', 'Pays', required=True)
    date_debut= fields.Datetime('Début validité')
    date_fin= fields.Datetime('Fin validité')
    employee_id= fields.Many2one('hr.employee', 'Employé', required=False)

class carte_sejour(models.Model):
    _name = "hr.carte.sejour"
    _description = "Carte de séjour employé"

    name= fields.Char('Libellé visa', size=64, required=False, readonly=False)
    reference= fields.Char('N° Visa', size=64, required=False, readonly=False)
    pays_id= fields.Many2one('res.country', 'Pays', required=False)
    date_debut= fields.Datetime('Début validité')
    date_fin= fields.Datetime('Fin validité')
    employee_id= fields.Many2one('hr.employee', 'Employé', required=False)

class enfants_employe(models.Model):
    _name = "hr.employee.enfant"
    _description = "Enfants de l'employé"
    
    name= fields.Char('Nom', size=128, required=True, readonly=False)
    date_naissance= fields.Date("Date de naissance")
    mobile= fields.Char('Portable', size=128, required=False, readonly=False)
    email=fields.Char('email', size=128, required=False, readonly=False)
    employee_id= fields.Many2one('hr.employee', 'Employé', required=False)

class hr_parent_employee(models.Model):
    _name="hr.parent.employe"
    _description = "les parents de l'employee"

    name= fields.Char('Nom', size=128, required=True, readonly=False)
    date_naissance= fields.Date("Date de naissance")
    mobile= fields.Char('Portable', size=128, required=False, readonly=False)
    email= fields.Char('email', size=128, required=False, readonly=False)
    employee_id= fields.Many2one('hr.employee', 'Employé', required=False)

class personne_contacted(models.Model):
    _name = 'hr.personne.contacted'
    _description = 'Personnes a contacter'


    name= fields.Char("Name",size=128,required=True)
    email= fields.Char("Email",size=128)
    portable= fields.Char('Portable',size=128,required=True)
    state= fields.Selection([('parent','Père / Mère'),('conjoint','Conjoint(e)'),
                    ('enfant','Enfant'),('other','Autres')], 'Type de lien', readonly=False)
    Lien= fields.Char("Le lien",siez=128)
    employee_id= fields.Many2one("hr.employee",'Employé')

class hr_employee(models.Model):
    @api.one
    def _get_part_igr(self):
        result = 0
        if self.marital :
            t1 =self.marital
            B38 = t1[0]
            B39 = self.children
            B40 = self.enfants_a_charge

            if ((B38 == "s") or (B38 == "d")):
                if (B39 == 0):
                    if (B40 != 0):
                        result = 1.5
                    else:
                        result = 1
                else:
                    if ((1.5 +  B39 * 0.5) > 5):
                        result = 5
                    else:
                        result = 1.5 + B39 * 0.5
            else:
                if (B38 == "m"):
                    if (B39 == 0):
                        result = 2
                    else:
                        if ((2 + 0.5 * B39) > 5):
                            result = 5
                        else:
                            result = 2 + 0.5 * B39
                else:
                    if (B38 == "w"):
                        if (B39 == 0):
                            if (B40 != 0):
                                result = 1.5
                            else:
                                result = 1
                        else:
                            if ((2 + B39 * 0.5) > 5):
                                result = 5
                            else:
                                result = 2 + 0.5 * B39
                    else:
                        result += 2 + 0.5 * B39
        self.part_igr = result

    @api.model
    def getInputsPayroll(self, contract, date_from, date_to):
        res = []
        print(res)
        primes = contract.hr_payroll_prime_ids
        for p in primes :
            if p.code == 'TRSP' :
                if p.montant_prime > 25000 :
                    val = {
                        'name': p.prime_id.name,
                        'code': p.code,
                        'amount': 25000,
                        'contract_id': contract.id,
                    }
                    res.append(val)
                    val = {
                        'name': "Prime de transport Imposable",
                        'code': "TRSP_IMP",
                        'amount': p.montant_prime - 25000,
                        'contract_id': contract.id,
                    }
                    res.append(val)
                else :
                    val = {
                        'name': p.prime_id.name,
                        'code': p.code,
                        'amount': p.montant_prime,
                        'contract_id': contract.id,
                    }
                    res.append(val)
            else :
                val = {
                    'name': p.prime_id.name,
                    'code': p.code,
                    'amount': p.montant_prime,
                    'contract_id': contract.id,
                }
                res.append(val)

        return res

    _inherit="hr.employee"

    matricule_cnps= fields.Char('Matricule CNPS',size=64)
    enfants_a_charge= fields.Integer("Nombre d'enfants à charge",required=True)
    pere= fields.Char('Nom du père', size=128, required=False, readonly=False)
    mere= fields.Char('Nom de la mère', size=128, required=False, readonly=False)
    grade= fields.Char('Grade', size=64, required=False, readonly=False)
    enfants_ids= fields.One2many('hr.employee.enfant', 'employee_id', 'Enfants', required=False)
    licence_ids= fields.One2many('hr.licence', 'employee_id', 'Licences des employés')
    diplome_ids= fields.One2many('hr.diplomes.employee', 'employee_id', 'Diplôme des employés')
    visa_ids= fields.One2many('hr.visa', 'employee_id', 'Visas des employés')
    carte_sejour_ids= fields.One2many('hr.carte.sejour', 'employee_id', 'Carte de séjour des employés')
    part_igr= fields.Float(compute=_get_part_igr,string='Part IGR')
    payment_method= fields.Selection([('espece','Espèces'),('virement','Virement bancaire'),('cheque','Chèques')],
                                                string='Moyens de paiement',required=True)
    date_entree= fields.Date("Date d'entrée")
    piece_identite_id= fields.Many2one("hr.piece.identite","Pièce d'identité")
    presonnes_contacted_ids= fields.One2many('hr.personne.contacted','employee_id','Personnes à contacter')
    parent_employee_ids= fields.One2many("hr.parent.employe",'employee_id','Les parents')
    recruitment_degree_id= fields.Many2one('hr.employee.degree',"Niveau d'étude")
    start_date = fields.Date("Date d'embauche", required=True)
    end_date = fields.Date("Date de depart", required=False)


