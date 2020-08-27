# -*- coding: utf-8 -*-
import time
import babel
from odoo import models, fields, api, tools, _
from datetime import datetime


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # #@api.model
    # def get_inputs(self, contracts, date_from, date_to):
    #     """This Compute the other inputs to employee payslip.
    #                        """
    #     res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)
    #     print(res)
    #     for contract in contracts :
    #         employee = contract.employee_id
    #         results = contract.getInputsPayroll(date_from, date_to)
    #         if results :
    #             res += results
    #     return res

