#-*- coding:utf-8 -*-

##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

# from openerp.osv import osv
# from openerp.report import report_sxw
#
# import time
# import time
# from datetime import date
# from datetime import datetime
# from datetime import timedelta
# from dateutil import relativedelta
#
#
# class payslip_report(report_sxw.rml_parse):
#
#     def __init__(self, cr, uid, name, context):
#         super(payslip_report, self).__init__(cr, uid, name, context)
#         self.localcontext.update({
#             'get_payslip_lines': self.get_payslip_lines,
#             'get_somme_rubrique': self.get_somme_rubrique,
#             'get_amount_rubrique': self.get_amount_rubrique,
#             'get_line': self.getLineByCode,
#             'getTauxByCode': self.getTauxByCode,
#         })
#
#     def get_payslip_lines(self, obj):
#         payslip_line = self.pool.get('hr.payslip.line')
#         res = []
#         ids = []
#         for id in range(len(obj)):
#             if obj[id].appears_on_payslip is True:
#                 ids.append(obj[id].id)
#         if ids:
#             res = payslip_line.browse(self.cr, self.uid, ids)
#         return res
#
#     def get_somme_rubrique(self, obj, code):
#
#         payslip_ids = self.pool.get('hr.payslip').search(self.cr, self.uid, [('employee_id','=',obj.employee_id.id)])
#         payslip_obj = self.pool.get('hr.payslip').browse(self.cr, self.uid, payslip_ids)
#
#         cpt=0
#         annee= obj.date_to[2:4]
#         print(annee)
#         for payslip in payslip_obj :
#             for line in payslip.line_ids :
#                 if line.salary_rule_id.code == code and obj.date_to >= payslip.date_to and  payslip.date_to[2:4]==annee :
#                     cpt += line.total
#         return cpt
#
#     def get_amount_rubrique(self,obj,rubrique):
#         for id in range(len(obj)):
#             line_ids=obj[id].line_ids
#             total=0
#             for line in line_ids :
#                 if line.code == rubrique :
#                     total = line.total
#             return total
#
#     def getTauxByCode(self,obj,rubrique):
#         for id in range(len(obj)):
#             taux = 0.0
#             lines = obj[id].line_ids
#             for line in lines:
#                 if line.code == rubrique:
#                     print line.rate
#                     taux = line.rate
#             return taux
#
#     def getLineByCode(self, obj, code):
#         for id in range(len(obj)):
#             lines=obj[id].line_ids
#             for line in lines:
#                 if line.code == code:
#                     return line
#
# class wrapped_report_payslip(osv.AbstractModel):
#     _name = 'report.hr_payroll_ci.report_payslip'
#     _inherit = 'report.abstract_report'
#     _template = 'hr_payroll_ci.report_payslip'
#     _wrapped_report_class = payslip_report
#
# #-*- coding:utf-8 -*-
# # Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


class PayslipCustomReport(models.AbstractModel):
    _name = 'report.hr_payroll_ci.report_payslip'

    def get_somme_rubrique(self, obj, code=''):

        payslip_ids = self.pool.get('hr.payslip').search(self.cr, self.uid, [('employee_id','=',obj.employee_id.id)])
        payslip_obj = self.pool.get('hr.payslip').browse(self.cr, self.uid, payslip_ids)

        cpt=0
        annee= obj.date_to[2:4]
        print(annee)
        for payslip in payslip_obj :
            for line in payslip.line_ids :
                if line.salary_rule_id.code == code and obj.date_to >= payslip.date_to and  payslip.date_to[2:4]==annee :
                    cpt += line.total
        return cpt

    def get_amount_rubrique(self,obj,rubrique=''):
        for id in range(len(obj)):
            line_ids=obj[id].line_ids
            total=0
            for line in line_ids :
                if line.code == rubrique :
                    total = line.total
            return total

    def getTauxByCode(self,obj,rubrique=''):
        for id in range(len(obj)):
            taux = 0.0
            lines = obj[id].line_ids
            for line in lines:
                if line.code == rubrique:
                    print line.rate
                    taux = line.rate
            return taux

    def getLineByCode(self, obj, code=''):
        for id in range(len(obj)):
            lines=obj[id].line_ids
            for line in lines:
                if line.code == code:
                    return line

    @api.model
    def render_html(self, docids, data=None):
        payslips = self.env['hr.payslip'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': 'hr.payslip',
            'docs': payslips,
            'data': data,
            'get_somme_rubrique': self.get_somme_rubrique(self, payslips, code=''),
            'get_amount_rubrique': self.get_amount_rubrique(self,payslips,rubrique=''),
            'get_line': self.getTauxByCode(self,payslips,rubrique=''),
            'getTauxByCode': self.getLineByCode(self, payslips, code=''),
        }
        return self.env['report'].render('hr_payroll_ci.report_payslip', docargs)

