# -*- coding: utf-8 -*-

from odoo import api, models, osv,fields
# from openerp import osv,fields,models, api
from odoo.tools.translate import _
from datetime import datetime


class model_contract(models.Model):

    _name= "hr.model.contract"
    _description=u"Modèle de contrat"


    @api.onchange('hr_convention_id')
    def on_change_convention_id(self):
        if self.hr_convention_id :
            return {'domain':{'hr_secteur_id':[('hr_convention_id','=',self.hr_convention_id.id)]}}
        else :
            return {'domain':{'hr_secteur_id':[('hr_convention_id','=',False)]}}


    @api.onchange('hr_secteur_id')
    def on_change_secteur_id(self):
        if self.hr_secteur_id :
            return {'domain':{'categorie_salariale':[('hr_secteur_activite_id','=', self.hr_secteur_id.id)]}}
        else :
            return {'domain':{'categorie_salariale':[('hr_secteur_activite_id','=',False)]}}
        


    @api.onchange("categorie_salariale")
    def change_categorie(self):
        res = {'value':{
                      'salaire_base':0,
                      }
            }
        if self.categorie_salariale and self.categorie_salariale.salaire_base:
            self.salaire_base= self.categorie_salariale.salaire_base
        else :
            self.salaire_base= 0

        

    name= fields.Char("Designation",size=128,required=True)
    salaire_base= fields.Integer("Salaire de base",required=True)
    prime_ids= fields.One2many("hr.payroll.prime.montant","model_contract_id","Primes")
    categorie_salariale= fields.Many2one("hr.categorie.salariale","Categorie salariale",required=True,
             domain="[('hr_secteur_activite_id', '=', secteur_activite_id)]")
    titre_poste= fields.Many2one("hr.job","Titre du Poste",required=True)
    type_contract= fields.Many2one("hr.contract.type","Type de conntract",required=True)
    structure_salariale= fields.Many2one('hr.payroll.structure',"Structure salariale",required=True)
    convention_id= fields.Many2one("hr.convention","Convention",required=True)
    secteur_activite_id= fields.Many2one("hr.secteur.activite","Secteur d'activité",required=True)


class contract_generate(models.Model):

    api.multi
    def generate_contract(self):
        contract_obj = self.env["hr.contract"]
        prime_obj= self.env['hr.payroll.prime.montant']
        for employee in self.employee_ids:
            vals={
              'name': "Contract %s"%employee.name,
              "wage": self.model_contract_id.salaire_base,
              "employee_id":employee.id,
              "sursalaire": 0,
              "categorie_salariale_id": self.model_contract_id.categorie_salariale.id,
              'job_id': self.model_contract_id.titre_poste.id,
              'struct_id': self.model_contract_id.structure_salariale.id,
              'hr_convention_id': self.model_contract_id.convention_id.id,
              'hr_secteur_id': self.model_contract_id.secteur_activite_id.id,
              'type_id': self.model_contract_id.type_contract.id,
            }

            contract = contract_obj.create(vals)
            for prime in self.model_contract_id.prime_ids :
                prime_values={
                          'prime_id':prime.prime_id.id,
                          'montant_prime':prime.montant_prime,
                          'contract_id':contract.id,
                          }
                prime_montant_id = prime_obj.create(prime_values)
            
    _name="hr.contract.generate"

    name= fields.Char("Name",size=128,required=True)
    model_contract_id= fields.Many2one("hr.model.contract",'Model',required=True)
    date_generate= fields.Datetime("Date de génération")
    employee_ids= fields.Many2many("hr.employee","hr_model_contract_rel","hr_model_contract_id","employee_id","Employees")


class hr_payroll_prime_montant(models.Model):
    _inherit = 'hr.payroll.prime.montant' 
    _name="hr.payroll.prime.montant"


    model_contract_id= fields.Many2one("hr.model.contract","Modèle de contrat")
