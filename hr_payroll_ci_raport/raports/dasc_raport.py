# -*- coding:utf-8

from datetime import datetime
from odoo import api, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, format_amount
from odoo.exceptions import ValidationError


class ReportHrDasc(models.AbstractModel):
    _name = "report.hr_payroll_ci_raport.report_dasc"

    def check_date(self, date_from, date_to):
        print('Checking date')
        d1 = datetime.strptime(date_from, '%Y-%m-%d')
        d2 = datetime.strptime(date_to, '%Y-%m-%d')
        if d1.month != 1 or d2.month != 12:
            raise ValidationError(_("Entrer une date d'exercice"))

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
        self.check_date(data['form']['date_from'], data['form']['date_to'])

        print(data['disa']['assurance_maternite'])

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data,
            'docs': docs,
            'date_from': date_from,
            'date_to': date_to,
            'format_amount': format_amount.manageSeparator,
        }
