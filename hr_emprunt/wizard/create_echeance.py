# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2012 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_emprunt
# ##############################################################################  -->

from odoo import api , fields, models

class echeance_memory(models.TransientModel):
    _name="echeance.memory"
    _columns={
              'name':fields.char("Libellé",size=128,required=True),
              #'employee_id':fields.many2one('hr.employee','Employé'),#une seule personne
              'montant_echeance' : fields.float('Montant',size=60,required=False),
              'date_remboursement_echeance' : fields.date('Date de remboursement'),
              'wizard_id':fields.many2one('create.echeance.wizard'),
              }
echeance_memory()

class create_echeance_wizard(models.TransientModel):
    _name="create.echeance.wizard"
    _columns={
              'emprunt_id':fields.many2one('hr.emprunt',required=True,string='Emprunt'),
              'echeance_ids':fields.one2many('echeance.memory','wizard_id','Echéances')
             }
    def action_add_echeance(self,cr,uid,ids,context=None):
       #raise osv.except_osv('helo id num',uid)   
        wizard=self.browse(cr,uid,ids[0])
        echeance_obj=self.pool.get('hr.echeance')
        for echeance in wizard.echeance_ids:
            echeance_obj.create(cr,uid,{'name': echeance.name,
                                        #'employee_id':echeance.employee_id.id,
                                        'montant_echeance':echeance.montant_echeance,
                                        'date_remboursement_echeance':echeance.date_remboursement_echeance,
                                         'emprunt_id':wizard.emprunt_id.id
                                       })
        return {}
    
    def _get_active_emprunt(self,cr,uid,context=None):
        return context.get('active_id')
    
    _defaults={
              'emprunt_id':_get_active_emprunt
              }
    
create_echeance_wizard()