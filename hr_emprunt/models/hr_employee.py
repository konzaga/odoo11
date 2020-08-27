#-*- coding:utf-8 -*-


from odoo import api, fields, models, _

class HrEmployee(models.Model):
    _inherit= 'hr.employee'


    loaning_ids= fields.One2many('hr.emprunt.loaning', 'employee_id', 'Écheanciers')
    demande_ids= fields.One2many('hr.emprunt.demande', 'employe_id', 'Demandes')


    def get_amount_emprunt(self, date_from, date_to):
        loaning_obj= self.env['hr.emprunt.loaning']
        amount = 0
        if date_from and date_to :
            loanings= loaning_obj.search([('employee_id', '=', self.id)])
            if loanings :
                for loaning in loanings :
                    #print loaning.echeance_ids
                    echeances = loaning.echeance_ids.filtered(lambda r: r.date_prevu <= date_to and r.date_prevu >= date_from)

                    if echeances :
                        amount= sum([ech.montant for ech in echeances])
        #print "mount total is %s" %amount
        return amount

    def getAdvancedSalaryMonthly(self, date_from, date_to):
        as_obj= self.env['hr.advance.salary']
        amount = 0
        if  date_from and date_to :
            advance_salaries = as_obj.search([('employee_id', '=', self.id)]).filtered(lambda r: r.date <= date_to and r.date >= date_from)
            if advance_salaries :
                amount = sum([ad.amount for ad in advance_salaries])
        return amount

    @api.model
    def getInputsPayroll(self, contract, date_from, date_to):
        res = super(HrEmployee, self).getInputsPayroll(contract, date_from, date_to)
        avs = self.getAdvancedSalaryMonthly(date_from, date_to)
        if avs != 0 :
            val = {
                'name': "Avance sur salaire",
                'code': "AVS",
                'amount': avs,
                'contract_id': contract.id,
            }
            res += [val]
        emprunts = self.get_amount_emprunt(date_from, date_to)
        if emprunts != 0 :
            val = {
                'name': "Emprunt à déduire sur le salaire",
                'code': "EMP",
                'amount': emprunts,
                'contract_id': contract.id,
            }
            res+= [val]
        return res
