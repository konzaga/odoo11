# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, format_amount

from itertools import groupby


class ReportHrPayroll(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.report_payroll'


    _codes_rules = []

    def _lines(self, date_from, date_to, company_id, type_employe):
        res = {}
        resultats = []
        _headers = ['NOM ET PRENOMS']
        rules = self.env['hr.salary.rule'].search([('appears_on_payroll', '=', True)])
        emp_obj = self.env['hr.employee']
        date_from = date_from
        date_to = date_to
        print ("---------------------------------------------------------------------------------------------------------")
        for rule in rules :
            print(rule.name)
            _headers.append(rule.name)
        print ("---------------------------------------------------------------------------------------------------------")
        self._codes_rules = rules.mapped(lambda r: r.code)
        res['codes'] = self._codes_rules
        res['headers'] = _headers
        self.env.cr.execute("SELECT id FROM hr_payslip WHERE (date_from between to_date(%s,'yyyy-mm-dd') AND "
            "to_date(%s,'yyyy-mm-dd')) AND (date_to between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) AND "
            "company_id = %s", (date_from, date_to, date_from, date_to, company_id ))
        payslip_ids = [x[0] for x in self._cr.fetchall()]
        if payslip_ids :
            #Trier les employés par type(mensuel, journalier, horaire ou tous les employés
            if type_employe == 'mensuel':
                payslips_sorted= self.env['hr.payslip'].browse(payslip_ids).sorted(key=lambda r: r.employee_id.name)
                payslips = payslips_sorted.filtered(lambda r: r.employee_id.type == 'm')
            if type_employe == 'journalier':
                payslips_sorted= self.env['hr.payslip'].browse(payslip_ids).sorted(key=lambda r: r.employee_id.name)
                payslips = payslips_sorted.filtered(lambda r: r.employee_id.type == 'j')
            if type_employe == 'horaire':
                payslips_sorted= self.env['hr.payslip'].browse(payslip_ids).sorted(key=lambda r: r.employee_id.name)
                payslips = payslips_sorted.filtered(lambda r: r.employee_id.type == 'h')
            if type_employe == 'all':
                payslips= self.env['hr.payslip'].browse(payslip_ids).sorted(key=lambda r: r.employee_id.name)
            print('!!!!!',payslips)
            for employee, lines in groupby(payslips, lambda l: l.employee_id):
                vals = {'NAME': employee.name, 'type': employee.type}
                print('!!!',vals)
                print(employee)
                slips = list(lines)
                for rule in self._codes_rules :
                    amount = 0.0
                    for slip in slips :
                        self.env.cr.execute("SELECT SUM(total) FROM hr_payslip_line WHERE slip_id=%s AND code=%s",
                                     (slip.id, rule))
                        result = self.env.cr.dictfetchall()
                        if result and result[0]['sum'] is None:
                            amount+= 0.0
                        else:
                            amount += result[0].get('sum')
                    print(amount)
                    vals[rule] = amount
                print(vals)
                resultats+=[vals]
        res['lines']= resultats
        print(res)
        return res

    def _lines_total(self, codes, lines):
        res = {}
        for code in codes :
            total = 0
            for line in lines :
                if line[code] is not None :
                    total+= line[code]
            res[code] = total
        return res

    @api.model
    def get_report_values(self, docids, data=None):
        self.model = data['model']
        docs = self.env[self.model].browse(data['ids'])
        print(data['form']['type_employe'])
        results = self._lines(data['form']['date_from'], data['form']['date_to'], data['form']['company_id'][0],
                              data['form']['type_employe'])
        lines = results['lines']
        codes = results['codes']
        headers = results['headers']
        lang_code = self.env.context.get('lang') or 'fr_FR'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        date_from = datetime.strptime(data['form']['date_from'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        date_to = datetime.strptime(data['form']['date_to'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        total = self._lines_total(codes, lines)

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'lines': lines,
            'lines_total': total,
            'codes': codes,
            'headers': headers,
            'time': time,
            'format_amount': format_amount.manageSeparator,
        }

