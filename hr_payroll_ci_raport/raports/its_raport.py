# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, format_amount

from itertools import groupby


class ReportHrPayrollDisa(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.report_hr_its'



    def formting_date(self, date):
        data={}
        dat = date
        d = dat.split('/')
        d1 = d[2]
        d2 = d1[2]
        d3 = d1[3]
        data[0] = d2
        data[1] = d3
        return data

    def get_trimestre(self, date):
        data={}
        if date:
            date = datetime.strptime(date, '%Y-%m-%d')
            for i in range(0,4):
                if date.month == 1 or date.month == 2 or date.month == 3:
                    data[i] = i+1

                if date.month == 4 or date.month == 5 or date.month == 6:
                    data[i] = i+1

                if date.month == 7 or date.month == 8 or date.month == 9:
                    data[i] = i+1

                if date.month == 10 or date.month == 11 or date.month == 12:
                    data[i] = i+1
            return data

    def get_month(self, date):
        date = datetime.strptime(date, '%Y-%m-%d')
        return date


    @api.model
    def get_report_values(self, docids, data=None):
        self.model = data['model']
        docs = self.env[self.model].browse(data['ids'])
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)
        date_format = lang_id.date_format
        date_from = datetime.strptime(data['form']['date_from'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        date_to = datetime.strptime(data['form']['date_to'], DEFAULT_SERVER_DATE_FORMAT).strftime(date_format)
        date_year = self.formting_date(date_from)
        trim = self.get_trimestre(data['form']['date_from'])
        date = self.get_month(data['form']['date_from'])
        assiette = data['assiette'].values()
        totalBrut = data['TotalBrut']
        RevNetImp = data['RevNetImp']
        BaseImp = data['BaseImp'].values()
        AmountBase = data['AmountBase']
        ComtributionEmp = data['ComtributionEmp']
        NetPaie = data['NetPaie']
        print(NetPaie)


        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'time': time,
            'date_year': date_year,
            'trim': trim,
            'date': date,
            'assiette': assiette,
            'totalBrut': totalBrut,
            'RevNetImp': RevNetImp,
            'BaseImp': BaseImp,
            'AmountBase': AmountBase,
            'ComtributionEmp': ComtributionEmp,
            'NetPaie':NetPaie,
            'format_amount': format_amount.manageSeparator,
        }

