# -*- coding:utf-8 -*-


from odoo import api, fields, models, exceptions


class HrPayrollInverse(models.TransientModel):
    _name = 'hr.payroll.inverse'

    def _get_lines(self):
        active_id = self._context.get('active_id')
        print(active_id)
        if active_id :
            slip= self.env['hr.payslip'].browse(active_id)
            if slip :
                return [
                    (0, 0, {'rule_id': input.id})
                    for input in slip.input_line_ids
                ]

        return []

    @api.one
    def computeSlip(self):
        # print self._context.get('active_id')
        payslip = self.env['hr.payslip'].browse(self._context.get('active_id'))
        print(payslip.name)
        print(self.line_ids)
        contract = payslip.contract_id
        print(contract.name)
        total_intrant = contract.wage
        input = self.line_ids[0].rule_id
        print(input.name)
        amount_add = 0
        for prime in contract.hr_payroll_prime_ids:
            total_intrant += prime.montant_prime

        if total_intrant > self.montant:
            raise exceptions.Warning('Le montant est inféreur aux intrants')
        else:
            structure_salariale = payslip.struct_id
            use_anc = False
            for rule in structure_salariale.rule_ids:
                if rule.code == 'PANC':
                    use_anc = True
            if self.type_calcul == 'brut':
                if use_anc:
                    prime_anciennete = 0.0
                    if 1 < contract.an_anciennete < 26:
                        prime_anciennete = 0.01 * contract.wage * contract.an_anciennete
                        total_intrant += prime_anciennete
                        input.amount = self.montant - total_intrant
                else:
                    input.amount = self.montant - total_intrant
            elif self.type_calcul == 'net':
                amount_add = input.amount
                net_amount = payslip.get_net_paye()
                print(net_amount)
                while net_amount != self.montant:
                    net_amount = payslip.get_net_paye()
                    print(net_amount)
                    # print net_amount
                    if net_amount < self.montant:
                        print(self.montant - net_amount)
                        amount_add += self.montant - net_amount
                    else:
                        print(net_amount - self.montant)
                        amount_add -= (net_amount - self.montant)
                    print(amount_add)
                    input.amount = amount_add
                    payslip.compute_sheet()


    line_ids = fields.One2many('hr.payroll.inverse.line', 'inverse_id', 'Lignes', required=False, default=_get_lines)
    type_calcul = fields.Selection([('brut', 'Par le brut'), ('net', 'Par le net')], 'Méthode de calcul', requred=True)
    montant = fields.Integer("Montant ")

class HrPayrollInverseLine(models.TransientModel):
    _name='hr.payroll.inverse.line'

    rule_id = fields.Many2one('hr.payslip.input', 'Règle salariale', required=False)
    inverse_id= fields.Many2one('hr.payroll.inverse','Calcul inverse', required=False)