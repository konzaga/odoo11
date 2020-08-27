#-*- coding:utf-8 -*-

import time
from dateutil.relativedelta import relativedelta
from odoo import models, api, fields, _, exceptions

class hr_demande(models.Model):
    _name = 'hr.emprunt.demande'
    _description = "Demande d'emprunt"

    def _default_employee(self):
        employee_id = self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_id
        # else :
        #     raise exceptions.Warning("L'utilisateur courant n'est pas lié à un employée")

    name= fields.Char("Libellé",size=150,required=True, states={'done':[('readonly',True)], 'cancel':[('readonly',True)]})
    employe_id= fields.Many2one('hr.employee', 'Employe',ondelete='cascade', default=_default_employee, index=True, readonly=False,
                                states={'done':[('readonly',True)], 'cancel':[('readonly',True)]})
    job_id= fields.Many2one('hr.job', 'Poste',ondelete='cascade', related='employe_id.job_id', readonly=True)
    user_id= fields.Many2one('res.users', 'Demandeur', required=True, related_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)
    motif_demande= fields.Char("Motif",size=150,required=False, states={'done':[('readonly',True)], 'cancel':[('readonly',True)]})
    montant_demande= fields.Float("Montant", size=20, required=True, states={'done':[('readonly',True)], 'cancel':[('readonly',True)]})
    date_demande= fields.Date("Date d'emprunt", states={'done':[('readonly',True)], 'cancel':[('readonly',True)]},  default=time.strftime('%Y-%m-%d'))
    date_echeance= fields.Date("Date d'échéance proposée", states={'done':[('readonly',True)], 'cancel':[('readonly',True)]})
    note= fields.Text('Notes', states={'done':[('readonly',True)], 'cancel':[('readonly',True)]})
    state= fields.Selection([('draft','Brouillon'), ('submitted','Soumis'), ('confirmed','Confirmé'), ('validated','Validé'),
                             ('echeance', 'Echéance'),('done','Clôturé'), ('cancel','Réfusée')],'Statut', default='draft')

    #_constraints=[(_check_quotite,"",['montant_demande'])]

    @api.multi
    def action_draft(self):
        self.state= 'draft'

    @api.multi
    def action_confirmed(self):
        self.state = 'confirmed'

    @api.multi
    def action_generate_loaning(self):
        emp_obj= self.env['hr.emprunt.loaning']
        for demande in self:
            emprunt = {
                       'name':'Emprunt de %s' % (demande.employe_id.name),
                       'employee_id':demande.employe_id.id,
                       'date_emprunt':time.strftime('%Y-%m-%d'),
                       'date_debut_remboursement': demande.date_demande,
                       'montant_emprunt':demande.montant_demande,
                    'total_emprunt': demande.montant_demande,
                       'statut_emprunt':False,
                       'option':'lineaire',
                       'state':'draft',
                       'demande_id':demande.id,
                   }
            emp_id = emp_obj.create(emprunt)
            modid = self.env['ir.model.data'].get_object_reference('hr_emprunt','emprunt_form_view')
            demande.state= 'echeance'
            result = {
                'name': _("Echéancier de paiement"),
                'view_mode': 'form',
                'view_id': modid[1],
                'view_type': 'form',
                'res_model': 'hr.emprunt.loaning',
                'type': 'ir.actions.act_window',
                'domain': '[]',
                'res_id':emp_id.id,
                'context': {'active_id': emp_id.id},
                'target': 'new',
            }

            return result

    @api.multi
    def action_submitted(self):
        self.state = 'submitted'

    @api.multi
    def action_validated(self):
        self.state = 'validated'

    @api.multi
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def action_submit_timetable(self):
        return True

    @api.multi
    def action_done(self):
        self.state = 'done'

    # _defaults = {
    #     'employe_id': _employee_get,
    #     'state': 'draft',
    #     'date_demande':time.strftime('%Y-%m-%d'),
    # }


class HrEmpruntLoaning(models.Model):
    _name = 'hr.emprunt.loaning'
    _description = 'Echeanciers de paiement'

    name= fields.Char("Libellé de l'emprunt",size=150,required=True)
    employee_id= fields.Many2one('hr.employee', 'Employé',required=True, ondelete='cascade')
    # job_id= fields.Many2one('hr.job', 'Poste', required=True)
    demande_id= fields.Many2one('hr.emprunt.demande', 'Demande',ondelete='cascade')
    echeance_ids= fields.One2many('hr.emprunt.loaning.line', 'loaning_id', 'Echéances')
    montant_emprunt= fields.Float("Montant emprunt", size=20, required=True)
    date_emprunt= fields.Date("Date d'emprunt")
    date_debut_remboursement= fields.Date('Date debut remboursement',required=True)
    date_echeance= fields.Date("Date d'échéance")
    statut_emprunt= fields.Boolean('Reglé')
    total_emprunt= fields.Float('Total à rembourser')
    remaining_emprunt= fields.Float(compte='_remaining_emprunt_percent', string='Taux remb. restant')
    taux= fields.Float("Taux d'emprunt", help="Taux d'intérêt de remboursement", default=0.0)
    option= fields.Selection([('lineaire','Linéaire')],'Option échéance',readonly=False,required=True)
    nb_echeance= fields.Integer("Nombre d'échéance(s)")
    intervalle_echeance= fields.Selection([('week','Hebdomadaire'),('month','Mensuel')],'Intervalle',readonly=False, default='month')
    notes= fields.Text('Notes')
    state= fields.Selection([('draft','Brouillon'),('demandeur', 'Demandeur'),('confirmed','Confirmé'), ('done','Terminé')],
                            'Status',readonly=False,required=True, default='draft')

    # @api.onchange('option')

    @api.onchange('montant_emprunt', 'taux')
    def compute_total_emprunt(self):
        if self.montant_emprunt!= 0:
            self.total_emprunt= self.montant_emprunt + (self.montant_emprunt*(self.taux/100))

    @api.onchange('employee_id', 'total_emprunt', 'option', 'date_debut_remboursement', 'nb_echeance', 'intervalle_echeance')
    def compute_lineaire_mode(self):
        """
        La fonction qui permet de calculer les écheanciers de paiement en fonction de l'option choisie
        :return: echeance_ids : list
        """
        quot_obj= self.env['hr.emprunt.quotite']
        lines = []
        self.echeance_ids = lines
        echeance = 0
        #Récuperer la quotité cessible pour l'employé en cours
        quotie = False
        if self.employee_id and self.employee_id.job_id :
            quotie= quot_obj.getQuotiteCessible(self.employee_id.job_id.id)
        if self.option == 'lineaire':
            if self.nb_echeance != 0:
                echeance= int(self.total_emprunt / self.nb_echeance)
                if echeance <= quotie.somme_max :
                    pass
                else :
                    raise exceptions.Warning("Le montant à rembourser de %s doit être inférieur à la quotité cessible "
                                             "qui est %s"%(echeance, quotie.somme_max))
            start= fields.Datetime.from_string(self.date_debut_remboursement)
            for i in range(self.nb_echeance):
                value = {
                    'name': 'Remboursement de %s/%s'%(start.month,start.year),
                    'date_prevu': start,
                    'date_remboursement_echeance': False,
                    'statut_echeance': 'take',
                    'montant': echeance
                }
                lines+=[value]
                if self.intervalle_echeance == 'month':
                    start+= relativedelta(months=+1)
                else :
                    start+= relativedelta(weeks=+1)
        else :
            pass
        self.echeance_ids = lines

    @api.multi
    def computeLoaning(self):
        self.ensure_one()
        if self.type == 'lineaire':
            return True
        else :
            return True

    @api.multi
    def echeance_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'hr_emprunt.report_echeancier')

    @api.one
    def action_demandeur(self):
        self.state = 'demandeur'

    @api.one
    def action_confirmed(self):
        if self.demande_id :
            self.demande_id.action_validated()
        self.state = 'done'

class HrEmpruntLoaningLine(models.Model):
    _name = 'hr.emprunt.loaning.line'
    _description = "Lignes d'echeanciers de paiement"

    @api.one
    def _get_solde_echeance(self):
        self.montant_restant = self.montant - self.montant_paye

    @api.one
    def action_suspendre(self):
        email_obj= self.env['mail.template']
        response =  email_obj.send_notification('hr_emprunt', self, 'emprunt_suspension_notif')
        if response :
            self.write({'statut_echeance': 'suspendu'})


    name= fields.Char('Nom', required=True)
    date_prevu= fields.Date('Date de prélèvement', required=True)
    date_remboursement_echeance= fields.Date('Date de paiement', required=False)
    montant= fields.Integer('Montant', required=True, default=0)
    montant_paye= fields.Integer('Montant payé', required=False, default=0)
    montant_restant= fields.Integer('Reste à payer', required=False, compute='_get_solde_echeance')
    statut_echeance= fields.Selection([('take', 'A prelever'), ('taked', 'Prélévé'), ('suspendu', 'Suspendu')], 'Status')
    loaning_id= fields.Many2one('hr.emprunt.loaning', 'Écheancier', required=False)
