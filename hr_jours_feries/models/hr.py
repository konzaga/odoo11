# -*- coding:utf-8 -*-


from odoo import api, fields, models, exceptions

class HrJourFerie(models.Model):
    _name = 'hr.jour.ferie'
    _description= """
        Gestion des jours feries
        """

    name= fields.Char('Libellé', required=True)
    date= fields.Date('Date', required=True)
    payroll_in= fields.Boolean('Chômer et payer', default=False)
    description= fields.Text('Description', required=False)