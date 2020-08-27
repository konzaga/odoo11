# -*- coding: utf-8 -*-


import time
from odoo import models, fields, api, osv
from datetime import datetime

class convention(models.Model):
    _name="hr.convention"
    _description="Convention"

    name= fields.Char("Name",size=128,required=True)
    description= fields.Text("Description")
    secteurs_ids= fields.One2many("hr.secteur.activite", "hr_convention_id", "Secteurs d'activtés")


class hr_secteur_activite(models.Model):
    _name="hr.secteur.activite"
    _description = "Secteur d'activite"


    name= fields.Char("Name",size=128,required=True)
    description= fields.Text("Description")
    hr_convention_id= fields.Many2one("hr.convention","Convention",required=True)
    salaire_ids= fields.One2many("hr.categorie.salariale","hr_secteur_activite_id","Catégories salariales")



class categorie_salariale(models.Model):
    _name = "hr.categorie.salariale"
    _description = "Categorie salariale"


    name= fields.Char('Libellé', size=64, required=False)
    salaire_base= fields.Integer("Salaire de base")
    description= fields.Text('Description')
    hr_secteur_activite_id= fields.Many2one('hr.secteur.activite', "Secteur d'activité")
    
