# -*- coding:utf-8 -*-


from odoo import models, api, fields, exceptions

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_inputs(self, contracts, date_from, date_to):

        res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)
        print(contracts)
        for contract in contracts:
            inputs = contract.employee_id.getInputsPayroll(contract, date_from, date_to)
            if inputs :
                res+= inputs
        return res



