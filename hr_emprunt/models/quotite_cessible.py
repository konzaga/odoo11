#-*- coding:utf-8 -*-

from odoo import api, fields, models

class hr_emprunt_quotite(models.Model):
    _name = 'hr.emprunt.quotite'
    _description = 'Quotités cessibles des emprunts'

    name= fields.Char('Désignation', size=64, required=False, readonly=False)
    job_id= fields.Many2one('hr.job', 'Poste', required=False)
    somme_min= fields.Float('Somme min')
    somme_max= fields.Float('Somme max')
    description= fields.Text('Description')

    def getQuotiteCessible(self, job_id):
        if job_id:
            quotite = self.search([('job_id', '=', job_id)], limit=1)
            return quotite
        return False