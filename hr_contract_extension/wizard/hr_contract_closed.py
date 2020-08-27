# -*- coding: utf-8 -*-


import time
from odoo import osv,fields, api, models
from odoo.tools.translate import _
from datetime import datetime


class hr_contract_closed(models.Model):
    _name="hr.contract.closed"
    _description = "contracts closed"

    name= fields.Selection([
                ('licenced','Licencement'),
                ('hard_licenced','Licencement faute grave'),
                ('ended','Fin de contract'),
                 ], 'Name', select=True),
    date_closing= fields.Datetime("Date de clôture",required=True)
    description= fields.Text("Description",required=True)
    date_create= fields.Datetime("Date de creation", default= lambda *a: time.strftime('%Y-%m-%d'))

    @api.one
    def cloture_contract(self):
        hr_contract_id=self._context.get('active_ids')
        hc_obj=self.env['hr.contract']
        hc_obj.write(hr_contract_id,{'date_end':i.date_closing,
                                                'description_cloture':i.description,
                                                'type_ended':i.name,
                                                'state':'ended',})
        return True