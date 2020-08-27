# -*- coding:utf-8 -*-

from odoo import models, api, fields, exceptions, _
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def getWorkedDays(self, date_from, date_to, contract):
        att_obj= self.env['hr.attendance']
        hours = 0
        if self.type in ('j', 'h'):
            self.env.cr.execute("SELECT id, check_in, check_out FROM hr_attendance WHERE (check_in"
                   " between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) AND"
                    "(check_out between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))"
                       " AND employee_id=%s",(date_from,date_to,date_from,date_to,self.id))
            for x in self.env.cr.dictfetchall():
                date_start = fields.Datetime.from_string(x['check_in'])
                date_end = fields.Datetime.from_string(x['check_out'])
                tmp = relativedelta(date_end, date_start)
                hours+= tmp.hours
            days = hours/8
            return {
                'name': _("Nombre de jours travaillés"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': days,
                 'number_of_hours': hours,
                 'contract_id': contract.id,
            }
        else :
            attendances = {
             'name': _("Normal Working Days paid at 100%"),
             'sequence': 1,
             'code': 'WORK100',
             'number_of_days': 30,
             'number_of_hours': 173.33,
             'contract_id': contract.id,
            }

            return attendances