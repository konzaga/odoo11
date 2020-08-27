# -*- coding: utf-8 -*-

from datetime import datetime
import time
from odoo import api, models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, format_amount

from itertools import groupby


class ReportHrCnpsMonthly(models.AbstractModel):
    _name = 'report.hr_payroll_ci_raport.cnps_trimestriel_report'

    def compute_all(self, data, tranche, code):
        for item in data :
            if item.get('tranche') == tranche:
                result = item.get(code)
                if result == 0 :
                    return ''
                else :
                    return result
        return ''

    def compute_total(self, data):
        amount = data['retraite'] + data['accident'] + data['famille'] + data['maternity']
        return int(amount)

    # @api.model
    # def render_html(self, docids, data=None):
    #     self.model = data['model']
    #     docs = self.env[self.model].browse(data['ids'])
    #     lang_code = self.env.context.get('lang') or 'en_US'
    #     lang = self.env['res.lang']
    #     lang_id = lang._lang_get(lang_code)
    #
    #     docargs = {
    #         'doc_ids': self.ids,
    #         'doc_model': self.model,
    #         'data': data,
    #         'docs': docs,
    #         'time': time,
    #         'compute_all': self.compute_all,
    #         'compute_total': self.compute_total,
    #         'format_amount': format_amount.manageSeparator,
    #     }
    #     return self.env['report'].render('hr_payroll_ci_raport.cnps_trimestriel_report', docargs)

    @api.model
    def get_report_values(self, docids, data=None):

        self.model = data['model']
        docs = self.env[self.model].browse(data['ids'])
        lang_code = self.env.context.get('lang') or 'en_US'
        lang = self.env['res.lang']
        lang_id = lang._lang_get(lang_code)

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data,
            'docs': docs,
            'time': time,
            'compute_all': self.compute_all,
            'compute_total': self.compute_total,
            'format_amount': format_amount.manageSeparator,
        }
