# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        print(res)

        for contract in contracts :
            print(contract)
            employee = contract.employee_id
            if employee :
                overtimes = employee.getOvertime(employee.id, contract.id, date_from, date_to)
                res +=  overtimes
        return res