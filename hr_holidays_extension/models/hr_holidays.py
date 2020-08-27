#-*- coding:utf-8 -*-

from odoo import fields, models, api
from collections import namedtuple
from calendar import monthrange
from datetime import datetime

class hr_holidays(models.Model):
    _inherit= 'hr.holidays'


    code= fields.Char('Code', size=4, required=False)

    @api.model
    def computeHoldaysByType(self,date_from, date_to, contract, employee_id):
        res = []
        Range = namedtuple('Range',['start','end'])
        hstatus = self.env['hr.holidays.status'].search([])
        r1=Range(start=date_from,end=date_to)
        self._cr.execute("SELECT id FROM hr_holidays WHERE ((date_from"
                       " between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')) OR (date_to"
                       " between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd')))"
                       " AND state='validate' AND payslip_status = TRUE  AND type='remove' AND employee_id='%s'",(str(date_from),str(date_to),
                           str(date_from), str(date_to), employee_id))
        holidays_ids = [x[0] for x in self._cr.fetchall()]
        if holidays_ids :
            holidays = self.browse(holidays_ids)
            print(holidays)
            for status in hstatus:
                days = 0
                temp = holidays.filtered(lambda r: r.holiday_status_id == status)
                for tp in temp :
                    print(tp.date_from)
                    old_date_from=datetime.strptime(tp.date_from[:10],'%Y-%m-%d')
                    old_date_to = datetime.strptime(tp.date_to[:10],'%Y-%m-%d')
                    r2=Range(start=old_date_from,end=old_date_to)
                    result = (min(r1.end, r2.end)  - max(r1.start,r2.start)).days + 1
                    if result > 0:
                        days+= result
                if days != 0 :
                    nb_days = monthrange(date_from.year, date_from.month)
                    if days == nb_days[1] :
                        days = 30
                    hours = days * 173.33/30
                    vals = {
                        'name': status.name,
                        'sequence': 5,
                        'code': status.code,
                        'number_of_days': days,
                        'number_of_hours': hours,
                        'contract_id': contract.id,

                    }
                    res+=[vals]
        return res


class HrHolidaysStatus(models.Model):
    _inherit = 'hr.holidays.status'

    code= fields.Char('Code', size=4, required=False)

__author__ = 'lekaizen'
