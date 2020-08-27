#-*- coding:utf-8 -*-

from odoo import api, fields, models, _

class NotifModel(models.Model):
    _name= 'notify.model'
    _description= 'Notify model'


    name= fields.Char("Libellé", required=True, size=255)
    line_ids= fields.One2many('notify.model.line', 'notif_id', 'Lignes', required=True)

class NotifModelLine(models.Model):
    _name= 'notify.model.line'
    _description= "Notify line model managment"

    type= fields.Selection([('an', 'Année'),('mois', 'Mois'),('day', 'Jours'), ('hours', 'Heures')],
           'Type', required=True)
    number= fields.Integer('Date', required=True, default=1)
    notif_id= fields.Many2one('notify.model', 'Notif')