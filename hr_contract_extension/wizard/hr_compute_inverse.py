#-*- coding:utf-8 -*-


import time
from datetime import datetime
from dateutil import relativedelta
from odoo import api, fields, models, exceptions


class HrReverseContract(models.TransientModel):
    _name = 'hr.reverse.contract'

    type_calcul = fields.Selection([('brut', 'Par le brut'),('net','Par le net')], 'Méthode de calcul', requred=True)
    montant = fields.Integer("Montant ")
    contract_id = fields.Many2one('hr.contract', 'Contrat')
    payslip = fields.Many2one('hr.payslip', 'Bulletin de paie')

    def createPayslip(self, contract):
        payslip_obj = self.env['hr.payslip']
        date_from = time.strftime('%Y-%m-01')
        date_to = str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10]
        struct_id = contract.struct_id.id
        inputs = payslip_obj.get_inputs(contract.id, date_from, date_to)
        input_line_ids = []
        if inputs :
            for input in inputs :
                temp = [0, False, input ]
                input_line_ids+=[temp]
            #print inputs

        worked_days = payslip_obj.get_worked_day_lines(contract.id, date_from, date_to)
        #print worked_days
        worked_days_line_ids = []
        if worked_days :
            for worked_day in worked_days:
                worked_day['contract_id']= contract.id
                temp = [0, False, worked_day]
                worked_days_line_ids+=[temp]
        vals = {
                'employee_id': contract.employee_id.id,
                'date_from': date_from,
                'date_to': date_to,
                'contract_id': contract.id,
                'struct_id': contract.struct_id.id,
                'input_line_ids': input_line_ids,
                'worked_days_line_ids': worked_days_line_ids,
            }
        #print vals
        payslip_id = payslip_obj.create(vals)
        #print payslip_id
        payslip_id.compute_sheet()
        return payslip_id

    @api.one
    def compute(self):

        # print self._context.get('active_id')
        contract = self.env['hr.contract'].browse(self._context.get('active_id'))
        total_intrant = contract.wage
        sursalaire = 0
        for prime in contract.hr_payroll_prime_ids :
            total_intrant+= prime.montant_prime

        if total_intrant > self.montant :
            raise exceptions.Warning('Le montant est inféreur aux intrants')
        else :
            structure_salariale = contract.struct_id
            use_anc = False
            for rule in structure_salariale.rule_ids:
                if rule.code == 'PANC':
                    use_anc = True
            if self.type_calcul == 'brut':
                if use_anc :
                    prime_anciennete = 0.0
                    if 1 < contract.an_anciennete < 26 :
                        prime_anciennete = 0.01 * contract.wage * contract.an_anciennete
                        total_intrant+=prime_anciennete
                        contract.sursalaire = self.montant - total_intrant
                else :
                    contract.sursalaire = self.montant - total_intrant
            elif self.type_calcul == 'net':
                payslip = self.createPayslip(contract)
                sursalaire = contract.sursalaire
                net_amount = payslip.get_net_paye()
                while net_amount != self.montant :
                    net_amount = payslip.get_net_paye()
                    #print net_amount
                    if net_amount < self.montant :
                        sursalaire += self.montant - net_amount
                    else :
                        sursalaire -= (net_amount - self.montant)
                    #print sursalaire
                    contract.write({'sursalaire': sursalaire})
                    payslip.compute_sheet()

__author__ = 'lekaizen'