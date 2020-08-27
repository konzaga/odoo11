# -*- coding: utf-8 -*-

import time
from odoo import api, fields, osv, exceptions, models
from datetime import datetime
from odoo.tools.translate import _

from dateutil.relativedelta import relativedelta


class hr_type_piece(models.Model):
    _name="hr.type.piece"
    _description="Type de pièce d'identité"


    name= fields.Char("Désignation",size=128,required=True)
    description= fields.Text("Description")


class hr_piece_identite(models.Model):
    _name="hr.piece.identite"
    _rec_name="numero_piece"
    _decription="Pièce d'identité"

    numero_piece = fields.Char("Numéro de la pièce",size=128,required=True)
    nature_piece= fields.Selection([('attestion',"Attestation d'indentité"),("carte_sejour","Carte de séjour"),
                                   ("cni","CNI"),("passeport","Passeport")],string="Nature",required=True)
    date_etablissement= fields.Date("Date d'établissement",required=True)
    autorite= fields.Char("Autorité",size=128)

class hr_contract(models.Model):

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.date_start = self.employee_id.start_date

    @api.multi
    def calcul_anciennete_actuel(self):
        anciennete={}
        self.ensure_one()
        this_date = today = datetime.today()
        start_date = fields.Datetime.from_string(self.employee_id.start_date)
        if self.date_end :
            end_date = fields.Datetime.from_string(self.date_end)
            this_date = min(today, end_date) + relativedelta(months=+self.mois_report, years=+self.an_report)
            #print this_date
        tmp = relativedelta(this_date, start_date)
        anciennete={
                'year_old':tmp.years,
                'month_old':tmp.months,
            }

        return anciennete


    @api.one
    def _get_anciennete(self):
        res={}
        anciennete=self.calcul_anciennete_actuel()
        if anciennete:
            self.an_anciennete= anciennete['year_old']
            self.mois_anciennete= anciennete['month_old']

        
    _inherit="hr.contract"

    expatried= fields.Boolean('Expatrié', default=False)
    an_report= fields.Integer('Année',size=2)
    mois_report= fields.Integer('Mois report')
    an_anciennete= fields.Integer("Nombre d'année", compute=_get_anciennete)
    mois_anciennete= fields.Integer('Nombre de mois', compute=_get_anciennete)
    anne_anc= fields.Integer('Année')
    categorie_id= fields.Many2one("hr.categorie.contract",'Catégorie')
    sursalaire= fields.Integer('SurSalaire',required=False)
    hr_convention_id= fields.Many2one('hr.convention',"Convention",required=False)
    hr_secteur_id= fields.Many2one('hr.secteur.activite',"Secteur d'activité",required=False)
    categorie_salariale_id= fields.Many2one('hr.categorie.salariale', 'Catégorie salariale', required=False)
    hr_payroll_prime_ids= fields.One2many("hr.payroll.prime.montant",'contract_id',"Primes")
    # state= fields.Selection([('draft','Draft'),('in_progress',"En cours"),('ended','Terminé'),('cancel','Annulé')]
    #                         ,'Eat du contrat', select=True, readonly=True, default="draft")
    type_ended= fields.Selection([('licenced','Licencement'),('hard_licenced','Licencement faute grave'),
                ('ended','Fin de contract'),], 'Type de clôture', select=True)
    description_cloture= fields.Text("Motif de Clôture")
    wage= fields.Integer('Salaire de base',required=True)



    @api.multi
    def validate_contract(self):
        return self.write({'state':'open'})


    @api.multi
    def closing_contract(self):
        view_id = self.pool.get('ir.model.data').get_object_reference(self._cr, self._uid, 'hr_contract_extension', 'hr_contract_closed_form_view')
        #raise osv.except_osv('Test',view_id)
    
        return {
                'name':_("Clôture de contrat"),
                'view_mode': 'form',
                'view_id': view_id[1],
                'view_type': 'form',
                'res_model': 'hr.contract.closed',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'domain': '[]',
                'context': self._context,
            }

    @api.multi
    def action_cancel(self):
        return self.write({'state':'cancel'})


    @api.onchange("hr_convention_id")
    def on_change_convention_id(self):
        if self.hr_convention_id :
            return {'domain':{'hr_secteur_id':[('hr_convention_id','=',self.hr_convention_id.id)]}}
        else :
            return {'domain':{'hr_secteur_id':[('hr_convention_id','=',False)]}}

    @api.onchange("hr_secteur_id")
    def on_change_secteur_id(self):
        if self.hr_secteur_id :
            return {'domain':{'categorie_salariale_id':[('hr_secteur_activite_id','=', self.hr_secteur_id.id)]}}
        else :
            return {'domain':{'categorie_salariale_id':[('hr_secteur_activite_id','=',False)]}}
        

    @api.onchange('categorie_salariale_id')
    def on_change_categorie_salariale_id(self):
        if self.categorie_salariale_id:
            self.wage= self.categorie_salariale_id.salaire_base



class hr_payroll_prime(models.Model):
    _name = "hr.payroll.prime"
    _description = "prime"

    name= fields.Char('name', size=64,required=True)
    code= fields.Char('Code', size=64, required=True)
    description= fields.Text('Description')



class hr_payroll_prime_montant(models.Model):

    @api.one
    @api.depends('prime_id')
    def _get_code_prime(self):
        if self.prime_id :
            self.code= self.prime_id.code
    
    _name="hr.payroll.prime.montant"

    prime_id= fields.Many2one('hr.payroll.prime','prime',required=True)
    code= fields.Char("Code",compute=_get_code_prime)
    contract_id= fields.Many2one('hr.contract','Contract')
    montant_prime= fields.Integer('Montant', required=True)



class hr_contract_type(models.Model):
    _inherit="hr.contract.type"
    _name="hr.contract.type"

    code= fields.Char("Code",siez=5,required=True)
