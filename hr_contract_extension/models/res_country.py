# -*- encoding: utf-8 -*-

##############################################################################
#
# Copyright (c) 2014 Veone - support.veone.net
# Author: Veone
#
# Fichier du module hr_payroll_ci
# ##############################################################################

from odoo import osv, fields, models, api

class res_country(models.Model):
    _inherit='res.country'
    
    nationalite= fields.Char('Nationalité', size=64, required=False, readonly=False)


class res_city(models.Model):
    _name="res.ville"
    _description='Ville'
    
    name= fields.Char('Ville', size=64, required=False, readonly=False)
    country_id= fields.Many2one('res.country', 'Pays', required=False)

class res_commune(models.Model):
    _name="res.commune"
    _description='Commune'
    
    name= fields.Char('Ville', size=64, required=False, readonly=False)
    ville_id= fields.Many2one('res.ville', 'Ville', required=False),



class res_quartier(models.Model):
    _name="res.quartier"
    _description='Quartier'
    
    name= fields.Char('Quartier', size=64, required=False, readonly=False)
    commune_id= fields.Many2one('res.commune', 'Commune', required=False)



class res_partner(models.Model):
    _inherit='res.partner'
    

    @api.onchange('ville_id')
    def onchange_ville_id(self):
        if not self.ville_id :
            return {}
        else :
            return {
                    'value' : {
                               'city': self.ville_id.name
                               }
                }
    
    
    ville_id= fields.Many2one('res.ville', 'Ville', required=False)
    commune_id= fields.Many2one('res.commune', 'Commune', required=False)
    quartier_id= fields.Many2one('res.quartier', 'Quartier', required=False)
    ilot= fields.Char('Ilot', size=64, required=False, readonly=False)
    lot= fields.Char('Lot', size=64, required=False, readonly=False)
