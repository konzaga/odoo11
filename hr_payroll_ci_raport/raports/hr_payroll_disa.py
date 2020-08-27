# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, format_amount

from itertools import groupby


class ReportHrPayrollDisa(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.report_hr_disa'


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
        lines = data['lines']
        line_ids = self.env['hr.disa.line'].search([])
        pages = self.env['hr.payroll.disa'].getDataByPage(line_ids, page_one=10, page=20)
        print('----page----',pages)
        print('----page----', pages.values())

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'pages': pages.values(),
            'time': time,
            'format_amount': format_amount.manageSeparator,
        }

